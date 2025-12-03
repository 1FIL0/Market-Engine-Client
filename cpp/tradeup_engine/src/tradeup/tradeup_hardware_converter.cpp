/*
* Market Engine Client
* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
* See LICENCE file.
*/

#include "tradeup_hardware_converter.hpp"
#include "market_item.hpp"
#include "market_item_memory.hpp"
#include "namespace.hpp"
#include "tradeup.hpp"

USE_NAMESPACE_TRADEUP_ENGINE

TRADEUP::TradeupCPU TRADEUP::GPU2CPU(const TRADEUP::TradeupGPU &tradeupGPU)
{
   TRADEUP::TradeupCPU tradeupCPU;

   for (int i = 0; i < tradeupGPU.totalInputSize; ++i) {
      tradeupCPU.inputs.push_back(tradeupGPU.inputs[i]);
   }
   for (int i = 0; i < tradeupGPU.totalOutputSize; ++i) {
      ITEM::MarketItem makeshiftOutput = ITEM::getItem(tradeupGPU.outputIDS[i]);
      makeshiftOutput.floatVal = tradeupGPU.outputFloats[i];
      makeshiftOutput.wear = tradeupGPU.outputFloats[i];
      makeshiftOutput.tradeUpChance = tradeupGPU.outputTradeupChances[i];
      tradeupCPU.outputs.push_back(makeshiftOutput);
   }
   
   tradeupCPU.avgInputFloat = tradeupGPU.avgInputFloat;
   tradeupCPU.normalizedAvgInputFloat = tradeupGPU.normalizedAvgInputFloat;
   tradeupCPU.totalInputPrice = tradeupGPU.totalInputPrice;
   tradeupCPU.profitability = tradeupGPU.profitability;
   tradeupCPU.chanceToProfit = tradeupGPU.chanceToProfit;
   tradeupCPU.profitabilitySteamTax = tradeupGPU.profitabilitySteamTax;
   tradeupCPU.chanceToProfitSteamTax = tradeupGPU.chanceToProfitSteamTax;
   return tradeupCPU;
}