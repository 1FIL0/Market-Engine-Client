#pragma once

#include "hasher.hpp"
#include "namespace.hpp"
#include <rapidjson/document.h>
#include <rapidjson/stringbuffer.h>
#include "tradeup.hpp"

START_ENGINE_NAMESPACE_MULTI(TRADEUP)

void initTradeupHandler(void);
void getKnownTradeupHashes(void);
void openTradeupsDocument(rapidjson::Document *doc);
void writeTradeup(TradeupCPU &tradeupCPU, const std::string &deviceName);
std::string hashTradeup(const TradeupCPU &tradeupCPU);
void handleDocumentOvercapacity(rapidjson::Document &doc, rapidjson::Value &dataVal);
bool tradeupExists(const std::string &tradeupHash);

END_ENGINE_NAMESPACE