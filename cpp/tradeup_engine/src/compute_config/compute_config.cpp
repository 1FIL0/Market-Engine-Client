#include "compute_config.hpp"
#include "file_handler.hpp"
#include "definitions.hpp"
#include "logger.hpp"
#include "namespace.hpp"
#include <rapidjson/rapidjson.h>
#include <rapidjson/document.h>
#include <string>

USE_NAMESPACE_SHARE
USE_NAMESPACE_TRADEUP_ENGINE

START_ENGINE_NAMESPACE_MULTI(COMP)
ComputeConfig computeConfig;
END_ENGINE_NAMESPACE

COMP::ComputeConfig::ComputeConfig(void)
{
    rapidjson::Document ccDoc;
    ccDoc.Parse(FILES::readFile(PATH_CONFIG_CLIENT_TRADEUP_ENGINE).c_str());

    const rapidjson::Value &gradesDoc = ccDoc["Compute Rarities"];
    for (rapidjson::SizeType i = 0; i < gradesDoc.Size(); ++i) {
        grades.push_back(gradesDoc[i].GetInt());
    }
    const rapidjson::Value &categoriesDoc = ccDoc["Compute Categories"];
    for (rapidjson::SizeType i = 0; i < categoriesDoc.Size(); ++i) {
        categories.push_back(categoriesDoc[i].GetInt());
    }
    batchSize = ccDoc["Batch Size"].GetInt();
    maxInputPrice = ccDoc["Max Input Price"].GetFloat();
    singleItem = ccDoc["Single Item Batch"].GetBool();
    profitMargin = ccDoc["Profit Margin"].GetFloat();
    computeMode = ccDoc["Compute Mode"].GetInt();

    const rapidjson::Value &devicesDoc = ccDoc["Devices"];
    for (rapidjson::SizeType i = 0; i < devicesDoc.Size(); ++i) {
        devices.push_back(devicesDoc[i].GetString());
    }

    maxTradeupsInFile = ccDoc["Max Tradeups In File"].GetInt();
    outputVerbose = ccDoc["Output Verbose"].GetBool();

    LOGGER::sendMessage("Loaded configs: " + std::string(PATH_CONFIG_CLIENT_TRADEUP_ENGINE));
}
