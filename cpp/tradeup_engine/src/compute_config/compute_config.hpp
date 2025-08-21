#pragma once

#include "namespace.hpp"
#include <string>
#include <vector>

START_ENGINE_NAMESPACE_MULTI(COMP)

enum COMPUTE_MODES {COMPUTE_MODE_CPU = 0, COMPUTE_MODE_GPUS};

class ComputeConfig {
private:

public:
    std::vector<std::string> devices;

    std::vector<int> categories;
    std::vector<int> grades;
    int batchSize;
    float maxInputPrice;
    bool singleItem;
    float profitMargin;

    int computeMode;
    int maxTradeupsInFile;

    bool outputVerbose;

    ComputeConfig();
};

extern ComputeConfig computeConfig;

END_ENGINE_NAMESPACE