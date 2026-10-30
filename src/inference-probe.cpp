// Newly authored reconstruction probe. This is not the historical quicktest.
// Usage: probe MODEL INPUT.f32le OUTPUT.json CPU|VitisAI MODEL_SHA INPUT_SHA
// The wrapper/operator must verify the supplied hashes against input files.
#include "onnxruntime_c_api.h"
#include "exclusive-output.hpp"
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static std::string quoted(const std::string& text) {
    std::string result = "\"";
    const char* hex = "0123456789abcdef";
    for (unsigned char c : text) {
        if (c == '"' || c == '\\') { result += '\\'; result += c; }
        else if (c < 32) { result += "\\u00"; result += hex[c >> 4]; result += hex[c & 15]; }
        else result += c;
    }
    return result + '"';
}

struct Resources {
    const OrtApi* api;
    explicit Resources(const OrtApi* api_in) : api(api_in) {}
    OrtEnv* env = nullptr;
    OrtSessionOptions* options = nullptr;
    OrtSession* session = nullptr;
    OrtMemoryInfo* memory = nullptr;
    OrtValue* input = nullptr;
    OrtAllocator* allocator = nullptr;
    std::vector<char*> names;
    std::vector<OrtValue*> outputs;
    ~Resources() {
        for (auto* v : outputs) if (v) api->ReleaseValue(v);
        for (auto* n : names) if (n && allocator) allocator->Free(allocator, n);
        if (input) api->ReleaseValue(input);
        if (memory) api->ReleaseMemoryInfo(memory);
        if (session) api->ReleaseSession(session);
        if (options) api->ReleaseSessionOptions(options);
        if (env) api->ReleaseEnv(env);
    }
    void check(OrtStatus* status) const {
        if (status) {
            std::string message = api->GetErrorMessage(status);
            api->ReleaseStatus(status);
            throw std::runtime_error(message);
        }
    }
};

int main(int argc, char** argv) {
    try {
        if (argc != 7) throw std::runtime_error("usage: probe MODEL INPUT OUTPUT CPU|VitisAI MODEL_SHA INPUT_SHA");
        const std::string provider = argv[4];
        if (provider != "CPU" && provider != "VitisAI") throw std::runtime_error("unsupported provider");
        for (int n : {5, 6}) {
            const std::string hash = argv[n];
            if (hash.size() != 64 || hash.find_first_not_of("0123456789abcdef") != std::string::npos)
                throw std::runtime_error("expected lowercase SHA-256");
        }
        ExclusiveOutput output_record(argv[3]);
        // Input is fixed at batch=1 for the historical model's symbolic batch.
        // This probe targets the recorded x86_64 host and little-endian f32 data.
        std::vector<float> input(1 * 3 * 32 * 32);
        std::ifstream stream(argv[2], std::ios::binary);
        stream.read(reinterpret_cast<char*>(input.data()), input.size() * sizeof(float));
        if (stream.gcount() != static_cast<std::streamsize>(input.size() * sizeof(float)) || stream.peek() != EOF)
            throw std::runtime_error("input must contain exactly 3072 float32 elements");
        for (float value : input) if (!std::isfinite(value)) throw std::runtime_error("nonfinite input");
        const OrtApiBase* base = OrtGetApiBase();
        if (!base) throw std::runtime_error("OrtGetApiBase failed");
        std::cout << "ONNX Runtime: " << base->GetVersionString() << std::endl;
        const OrtApi* api = base->GetApi(ORT_API_VERSION);
        if (!api) throw std::runtime_error("ORT C API version mismatch");
        Resources r(api);
        r.check(api->CreateEnv(ORT_LOGGING_LEVEL_INFO, "reconstruction-probe", &r.env));
        r.check(api->CreateSessionOptions(&r.options));
        if (provider == "VitisAI") {
            r.check(api->SessionOptionsAppendExecutionProvider(r.options, "VitisAI", nullptr, nullptr, 0));
            std::cout << "Vitis AI EP registration: PASS" << std::endl;
        }
        r.check(api->CreateSession(r.env, argv[1], r.options, &r.session));
        std::cout << "ONNX session creation: PASS" << std::endl;
        r.check(api->CreateCpuMemoryInfo(OrtArenaAllocator, OrtMemTypeDefault, &r.memory));
        const int64_t shape[] = {1, 3, 32, 32};
        r.check(api->CreateTensorWithDataAsOrtValue(r.memory, input.data(), input.size() * sizeof(float), shape, 4,
                                                ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT, &r.input));
        size_t count = 0;
        r.check(api->SessionGetOutputCount(r.session, &count));
        if (count != 1) throw std::runtime_error("expected one output for the pinned model");
        r.check(api->GetAllocatorWithDefaultOptions(&r.allocator));
        r.names.resize(count, nullptr);
        r.outputs.resize(count, nullptr);
        std::vector<const char*> output_names(count);
        for (size_t i = 0; i < count; ++i) {
            r.check(api->SessionGetOutputName(r.session, i, r.allocator, &r.names[i]));
            output_names[i] = r.names[i];
        }
        const char* input_names[] = {"input"};
        const OrtValue* values[] = {r.input};
        r.check(api->Run(r.session, nullptr, input_names, values, 1, output_names.data(), count, r.outputs.data()));
        std::cout << "Inference: PASS" << std::endl;
        OrtTensorTypeAndShapeInfo* info = nullptr;
        r.check(api->GetTensorTypeAndShape(r.outputs[0], &info));
        ONNXTensorElementDataType type;
        size_t rank = 0;
        // Release type metadata even when a subsequent check throws.
        try {
            r.check(api->GetTensorElementType(info, &type));
            r.check(api->GetDimensionsCount(info, &rank));
            if (type != ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT || rank != 2)
                throw std::runtime_error("expected float32 rank-2 output");
            int64_t dims[2];
            r.check(api->GetDimensions(info, dims, 2));
            if (dims[0] != 1 || dims[1] != 10) throw std::runtime_error("expected output shape [1,10]");
        } catch (...) { api->ReleaseTensorTypeAndShapeInfo(info); throw; }
        api->ReleaseTensorTypeAndShapeInfo(info);
        float* output = nullptr;
        r.check(api->GetTensorMutableData(r.outputs[0], reinterpret_cast<void**>(&output)));
        for (int i = 0; i < 10; ++i) if (!std::isfinite(output[i])) throw std::runtime_error("nonfinite output");
        std::ostringstream result;
        result << "{\"model_sha256\":" << quoted(argv[5]) << ",\"input_sha256\":" << quoted(argv[6])
               << ",\"onnxruntime_version\":" << quoted(base->GetVersionString())
               << ",\"provider\":" << quoted(provider) << ",\"outputs\":[{\"name\":" << quoted(r.names[0])
               << ",\"shape\":[1,10],\"dtype\":\"float32\",\"values\":[";
        result << std::setprecision(std::numeric_limits<float>::max_digits10);
        for (int i = 0; i < 10; ++i) { if (i) result << ','; result << output[i]; }
        result << "]}]}\n";
        output_record.publish(result.str());
        std::cout << "Quicktest: PASS" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "FAIL: " << e.what() << std::endl;
        return 1;
    }
}
