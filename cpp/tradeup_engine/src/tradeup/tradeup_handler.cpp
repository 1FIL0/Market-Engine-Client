#include "tradeup_handler.hpp"
#include "compute_config.hpp"
#include "definitions.hpp"
#include "hasher.hpp"
#include "file_handler.hpp"
#include <algorithm>
#include <rapidjson/document.h>
#include <rapidjson/prettywriter.h>
#include <rapidjson/rapidjson.h>
#include <string>
#include "logger.hpp"
#include "market_item_memory.hpp"
#include "cpu_operations.hpp"
#include "time.hpp"
#include "tradeup.hpp"
#include <algorithm>
#include <vector>

USE_NAMESPACE_TRADEUP_ENGINE
USE_NAMESPACE_SHARE

std::vector<std::string> g_knownTradeupHashes;

void TRADEUP::initTradeupHandler(void)
{
    getKnownTradeupHashes();
}

void TRADEUP::getKnownTradeupHashes(void)
{
    LOGGER::sendMessage("Getting Known Tradeup Hashes");
    rapidjson::Document doc;
    openTradeupsDocument(&doc);
    rapidjson::Value &dataVal = doc["DATA"];

    LOGGER::sendMessage("Total Tradeups: " + std::to_string(dataVal.Size()));
    for (rapidjson::SizeType i = 0; i < dataVal.Size(); ++i) {
        rapidjson::Value &entry = dataVal[i];
        std::string hash(entry["Tradeup Hash"].GetString());
        g_knownTradeupHashes.push_back(hash);
    }
    LOGGER::sendMessage("Total Hashes: " + std::to_string(g_knownTradeupHashes.size()));
}

void TRADEUP::openTradeupsDocument(rapidjson::Document *doc)
{
    doc->Parse(FILES::readFile(PATH_DATA_CLIENT_PROFITABLE_TRADEUPS).c_str());
    rapidjson::Document::AllocatorType &allocator = doc->GetAllocator();
    
    if (!doc->HasMember("DATA")) {
        doc->RemoveAllMembers();
        doc->SetObject();
        doc->AddMember("DATA", rapidjson::Value(rapidjson::kArrayType), allocator);
    }
}

void TRADEUP::writeTradeup(TRADEUP::TradeupCPU &tradeupCPU, const std::string &deviceName)
{
    LOGGER::sendMessage("Writing Tradeup to file");

    // Sort in the same order to ensure same hash and prevent duplicates 

    auto &inputs = tradeupCPU.inputs;
    auto &outputs = tradeupCPU.outputs;
    std::sort(inputs.begin(), inputs.end());
    std::sort(outputs.begin(), outputs.end());

    std::string tradeupHash = TRADEUP::hashTradeup(tradeupCPU);
    if (tradeupExists(tradeupHash)) {
        LOGGER::sendMessage("Tradeup Already Exists: " + tradeupHash);
        return;
    }
    g_knownTradeupHashes.push_back(tradeupHash);

    rapidjson::Document doc;
    openTradeupsDocument(&doc);
    rapidjson::Document::AllocatorType &allocator = doc.GetAllocator();
    rapidjson::Value &dataVal = doc["DATA"];

    rapidjson::Value tradeupVal(rapidjson::kObjectType);
    rapidjson::Value inputsArrayDoc(rapidjson::kArrayType);
    rapidjson::Value outputsArrayDoc(rapidjson::kArrayType);

    tradeupVal.AddMember("Tradeup Hash", rapidjson::Value().SetString(tradeupHash.c_str(), allocator), allocator);
    tradeupVal.AddMember("Favourite", rapidjson::Value().SetBool(false), allocator);
    tradeupVal.AddMember("Date Found", rapidjson::Value().SetString(TIME::getCurrentDateTime().c_str(), allocator), allocator);
    tradeupVal.AddMember("Device Used", rapidjson::Value().SetString(deviceName.c_str(), allocator), allocator);
    tradeupVal.AddMember("Tradeup Category", rapidjson::Value().SetString(DEFINITIONS::categoryToString(inputs[0].category).c_str(), allocator), allocator);
    tradeupVal.AddMember("Tradeup Grade", rapidjson::Value().SetString(DEFINITIONS::gradeToString(inputs[0].grade).c_str(), allocator), allocator);
    for (auto &input : inputs) {
        rapidjson::Value inputDoc(rapidjson::kObjectType);
        auto inputItemColdData = ITEM::getColdData(input);
        inputDoc.AddMember("Perm ID", rapidjson::Value().SetUint64(input.permID), allocator);
        inputDoc.AddMember("Weapon", rapidjson::Value().SetString(inputItemColdData.weaponName.c_str(), allocator), allocator);
        inputDoc.AddMember("Skin", rapidjson::Value().SetString(inputItemColdData.skinName.c_str(), allocator), allocator);
        inputDoc.AddMember("Price", rapidjson::Value().SetFloat(input.price), allocator);
        inputDoc.AddMember("Price Steam Tax", rapidjson::Value().SetFloat(input.priceSteamTax), allocator);
        inputDoc.AddMember("Category", rapidjson::Value().SetInt(input.category), allocator);
        inputDoc.AddMember("Grade", rapidjson::Value().SetInt(input.grade), allocator);
        inputDoc.AddMember("Wear", rapidjson::Value().SetInt(input.wear), allocator);
        inputDoc.AddMember("Float Val", rapidjson::Value().SetFloat(input.floatVal), allocator);
        inputsArrayDoc.PushBack(inputDoc, allocator);
    }
    tradeupVal.AddMember("Inputs", inputsArrayDoc, allocator);
    tradeupVal.AddMember("Average Input Float", rapidjson::Value().SetFloat(tradeupCPU.avgInputFloat), allocator);
    tradeupVal.AddMember("Total Input Cost", rapidjson::Value().SetFloat(tradeupCPU.totalInputPrice), allocator);
    for (auto &output : outputs) {
        rapidjson::Value outputDoc(rapidjson::kObjectType);
        auto outputItemColdData = ITEM::getColdData(output);
        outputDoc.AddMember("Perm ID", rapidjson::Value().SetUint64(output.permID), allocator);
        outputDoc.AddMember("Weapon", rapidjson::Value().SetString(outputItemColdData.weaponName.c_str(), allocator), allocator);
        outputDoc.AddMember("Skin", rapidjson::Value().SetString(outputItemColdData.skinName.c_str(), allocator), allocator);
        outputDoc.AddMember("Price", rapidjson::Value().SetFloat(output.price), allocator);
        outputDoc.AddMember("Price Steam Tax", rapidjson::Value().SetFloat(output.priceSteamTax), allocator);
        outputDoc.AddMember("Category", rapidjson::Value().SetInt(output.category), allocator);
        outputDoc.AddMember("Grade", rapidjson::Value().SetInt(output.grade), allocator);
        outputDoc.AddMember("Wear", rapidjson::Value().SetInt(output.wear), allocator);
        outputDoc.AddMember("Float Val", rapidjson::Value().SetFloat(output.floatVal), allocator);
        outputDoc.AddMember("Output Amount", rapidjson::Value().SetInt(output.outputAmount), allocator);
        outputDoc.AddMember("Tradeup Chance", rapidjson::Value().SetFloat(output.tradeUpChance), allocator);
        outputDoc.AddMember("Money Gain", rapidjson::Value().SetFloat(output.price - tradeupCPU.totalInputPrice), allocator);
        outputDoc.AddMember("Money Gain Steam Tax", rapidjson::Value().SetFloat(output.priceSteamTax - tradeupCPU.totalInputPrice), allocator);
        outputsArrayDoc.PushBack(outputDoc, allocator);
    }
    tradeupVal.AddMember("Outputs", outputsArrayDoc, allocator);
    tradeupVal.AddMember("Total Outputs", rapidjson::Value().SetInt(outputs.size()), allocator);
    tradeupVal.AddMember("Chance To Profit", rapidjson::Value().SetFloat(tradeupCPU.chanceToProfit), allocator);
    tradeupVal.AddMember("Profitability", rapidjson::Value().SetFloat(tradeupCPU.profitability), allocator);
    tradeupVal.AddMember("Chance To Profit Steam Tax", rapidjson::Value().SetFloat(tradeupCPU.chanceToProfitSteamTax), allocator);
    tradeupVal.AddMember("Profitability Steam Tax", rapidjson::Value().SetFloat(tradeupCPU.profitabilitySteamTax), allocator);

    dataVal.PushBack(tradeupVal, allocator);

    TRADEUP::handleDocumentOvercapacity(doc, dataVal);
    rapidjson::StringBuffer docBuffer;
    rapidjson::PrettyWriter<rapidjson::StringBuffer> finalWriter(docBuffer);
    doc.Accept(finalWriter);
    
    FILES::writeFileAtomic(PATH_DATA_CLIENT_PROFITABLE_TRADEUPS_TEMP, std::string(docBuffer.GetString()));
}

std::string TRADEUP::hashTradeup(const TRADEUP::TradeupCPU &tradeupCPU)
{
    std::string hashInput = "";
    for (auto &input : tradeupCPU.inputs) {
        auto coldData = ITEM::getColdData(input);
        hashInput += coldData.weaponName + coldData.skinName;
        hashInput += input.category;
        hashInput += input.wear;
        hashInput += input.price;
    }
    for (auto &output : tradeupCPU.outputs) {
        auto coldData = ITEM::getColdData(output);
        hashInput += coldData.weaponName + coldData.skinName;
        hashInput += output.category;
        hashInput += output.wear;
        hashInput += output.price;
        hashInput += output.tradeUpChance;
    }
    hashInput += tradeupCPU.profitability;
    hashInput += tradeupCPU.chanceToProfit;
    const std::string digest = HASHER::sha256(hashInput);
    return digest;
}

void TRADEUP::handleDocumentOvercapacity(rapidjson::Document &doc, rapidjson::Value &dataVal)
{
    auto config = COMP::computeConfig;
    if (dataVal.Size() < (unsigned)config.maxTradeupsInFile) {
        return;
    }

    float lowestProfitability = 0;
    rapidjson::SizeType leastProfitableIndex = 0;

    for (rapidjson::SizeType i = 0; i < dataVal.Size(); ++i) {
        const rapidjson::Value &tradeupCPU = dataVal[i];
        if (tradeupCPU["Profitability"].GetFloat() < lowestProfitability && !tradeupCPU["Favourite"].GetBool()) {
            lowestProfitability = tradeupCPU["Profitability"].GetFloat();
            leastProfitableIndex = i;
        } 
    }

    dataVal.Erase(dataVal.Begin() + leastProfitableIndex);
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    doc.Accept(writer);
}

bool TRADEUP::tradeupExists(const std::string &tradeupHash)
{
    for (auto &hash : g_knownTradeupHashes) {
        if (hash == tradeupHash) {
            return true;
        }
    }

    return false;
}
