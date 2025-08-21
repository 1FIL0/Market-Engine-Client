#include "tradeup_hardware_converter.hpp"
#include "namespace.hpp"
#include "tradeup.hpp"

USE_NAMESPACE_TRADEUP_ENGINE

TRADEUP::TradeupCPU TRADEUP::GPU2CPU(const TRADEUP::TradeupGPU &tradeupGPU)
{
   TRADEUP::TradeupCPU tradeupCPU;

   for (int i = 0; i < MAX_GPU_TRADEUP_INPUTS; ++i) {
      tradeupCPU.inputs.push_back(tradeupGPU.inputs[i]);
   }
   for (int i = 0; i < tradeupGPU.totalOutputSize; ++i) {
      tradeupCPU.outputs.push_back(tradeupGPU.outputs[i]);
   }
   
   tradeupCPU.avgInputFloat = tradeupGPU.avgInputFloat;
   tradeupCPU.totalInputPrice = tradeupGPU.totalInputPrice;
   tradeupCPU.profitability = tradeupGPU.profitability;
   tradeupCPU.chanceToProfit = tradeupGPU.chanceToProfit;
   tradeupCPU.profitabilitySteamTax = tradeupGPU.profitabilitySteamTax;
   tradeupCPU.chanceToProfitSteamTax = tradeupGPU.chanceToProfitSteamTax;
   return tradeupCPU;
}