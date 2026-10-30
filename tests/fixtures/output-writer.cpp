// Standalone test driver: no ONNX Runtime, SDK, compiler plugin, or device API.
#include "exclusive-output.hpp"
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
    try {
        if (argc < 3) return 2;
        ExclusiveOutput output(argv[1]);
        if (argc == 4 && std::string(argv[3]) == "--fail")
            throw std::runtime_error("fixture failure before publication");
        std::cout << "READY" << std::endl;
        if (argc == 4 && std::string(argv[3]) == "--wait") std::cin.get();
        output.publish(argv[2]);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
