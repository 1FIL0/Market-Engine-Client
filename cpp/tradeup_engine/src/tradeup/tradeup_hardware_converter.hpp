#pragma once

#include "namespace.hpp"
#include "tradeup.hpp"

START_ENGINE_NAMESPACE_MULTI(TRADEUP)

TradeupCPU GPU2CPU(const TradeupGPU &tradeupGPU);

END_ENGINE_NAMESPACE