// Device-independent, no-replace publication of a complete result record.
#pragma once
#include <atomic>
#include <cerrno>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

class ExclusiveOutput {
    int parent_ = -1;
    int file_ = -1;
    std::string destination_;
    std::string temporary_;
    static std::runtime_error error(const char* context) {
        return std::runtime_error(std::string(context) + ": " + std::strerror(errno));
    }
    void cleanup() noexcept {
        if (parent_ >= 0 && file_ >= 0 && !temporary_.empty()) {
            struct stat owned{}, current{};
            if (::fstat(file_, &owned) == 0 &&
                ::fstatat(parent_, temporary_.c_str(), &current, AT_SYMLINK_NOFOLLOW) == 0 &&
                owned.st_dev == current.st_dev && owned.st_ino == current.st_ino)
                ::unlinkat(parent_, temporary_.c_str(), 0);
        }
        if (file_ >= 0) ::close(file_);
        if (parent_ >= 0) ::close(parent_);
        file_ = parent_ = -1;
    }
public:
    explicit ExclusiveOutput(const std::filesystem::path& output) {
        try {
            destination_ = output.filename().string();
            if (destination_.empty() || destination_ == "." || destination_ == "..")
                throw std::runtime_error("invalid output leaf");
            auto parent = output.parent_path();
            if (parent.empty()) parent = ".";
            parent_ = ::open(parent.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (parent_ < 0) throw error("open output parent");
            struct stat info{};
            if (::fstatat(parent_, destination_.c_str(), &info, AT_SYMLINK_NOFOLLOW) == 0)
                throw std::runtime_error("output exists; preserved without change");
            if (errno != ENOENT) throw error("inspect output");
            static std::atomic<unsigned long> sequence{0};
            for (int attempt = 0; attempt < 16; ++attempt) {
                temporary_ = ".npu-result-" + std::to_string(::getpid()) + "-" +
                             std::to_string(sequence.fetch_add(1));
                file_ = ::openat(parent_, temporary_.c_str(),
                                 O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
                if (file_ >= 0) return;
                if (errno != EEXIST) throw error("create private output");
            }
            throw std::runtime_error("cannot reserve unique private output");
        } catch (...) { cleanup(); throw; }
    }
    ExclusiveOutput(const ExclusiveOutput&) = delete;
    ExclusiveOutput& operator=(const ExclusiveOutput&) = delete;
    ~ExclusiveOutput() { cleanup(); }
    void publish(const std::string& data) {
        if (file_ < 0 || temporary_.empty()) throw std::runtime_error("output already finalized");
        size_t offset = 0;
        while (offset < data.size()) {
            ssize_t wrote = ::write(file_, data.data() + offset, data.size() - offset);
            if (wrote < 0 && errno == EINTR) continue;
            if (wrote <= 0) throw error("write private output");
            offset += static_cast<size_t>(wrote);
        }
        if (::fsync(file_) != 0) throw error("flush private output");
        if (::linkat(parent_, temporary_.c_str(), parent_, destination_.c_str(), 0) != 0)
            throw error("publish output without replacement");
        cleanup();
        temporary_.clear();
    }
};
