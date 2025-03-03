## Strategy

```
//pinescript
//@version=6
strategy('Lamba Strategy', overlay = true, initial_capital = 300, pyramiding = 2, currency = currency.USDT, default_qty_type = strategy.cash, default_qty_value = 100)

takeProfitPercent = input.float(0.5, step = .1, title = 'TAKE %')
durationTrigger = input.int(300, title = 'Duration TRIGGER')

ema50 = ta.ema(close, 50)
ema200 = ta.ema(close, 200)
rsi = ta.rsi(close, 14)

is_uptrend = ema50 > ema200
is_downtrend = ema50 < ema200

var int trend_duration = 0

if is_uptrend and not is_uptrend[1]
    trend_duration := 1
else if is_downtrend and not is_downtrend[1]
    trend_duration := 1
else if is_uptrend
    trend_duration := trend_duration + 1
else if is_downtrend
    trend_duration := trend_duration + 1

var bool watch_short = false
var bool watch_long = false

if is_uptrend and trend_duration % durationTrigger == 0
    watch_short := true
if is_downtrend and trend_duration % durationTrigger == 0
    watch_long := true

if is_uptrend
    watch_long := false
if is_downtrend
    watch_short := false

long_percentage = ((strategy.position_avg_price - close) / strategy.position_avg_price * 100)
short_percentage = ((close - strategy.position_avg_price) / strategy.position_avg_price * 100)

if watch_short and rsi > 70 and strategy.position_size == 0
    strategy.entry('Short', strategy.short)

if watch_short and rsi > 70 and strategy.position_size < 0 and short_percentage > 1.2
    strategy.entry('Short', strategy.short)

if watch_long and rsi < 30 and strategy.position_size == 0
    strategy.entry('Long', strategy.long)

if watch_long and rsi < 30 and strategy.position_size > 0 and long_percentage > 1.2
    strategy.entry('Long', strategy.long)


if strategy.position_size > 0 and strategy.openprofit_percent > takeProfitPercent
    strategy.close('Long')
if strategy.position_size < 0 and strategy.openprofit_percent > takeProfitPercent
    strategy.close('Short')

plot(ema50, title = 'ema50', color = color.yellow, linewidth = 1, style = plot.style_cross)
plot(ema200, title = 'ema200', color = ema50 > ema200 ? color.green : color.red, linewidth = 2)

```

## Indicator

```
//pinescript
//@version=6
indicator('Lamba indicator', overlay = false)

ema50 = ta.ema(close, 50)
ema200 = ta.ema(close, 200)
rsi = ta.rsi(close, 14)

plot(rsi)

var int trend_duration = 0

is_uptrend = ema50 > ema200
is_downtrend = ema50 < ema200

if is_uptrend and not is_uptrend[1]
    trend_duration := 1
else if is_downtrend and not is_downtrend[1]
    trend_duration := 1
else if is_uptrend
    trend_duration := trend_duration + 1
else if is_downtrend
    trend_duration := trend_duration + 1

plot(trend_duration, title="Trend Duration", color=is_uptrend ? color.green : color.red, linewidth=2)


var bool watch_short = false
var bool watch_long = false

if is_uptrend and trend_duration % 300 == 0
    watch_short := true
   
if is_downtrend and trend_duration % 300 == 0
    watch_long := true
    
plot(watch_short and rsi > 70 ? 300 : 0, title = 'SHORT', color = color.red)
plot(watch_long and rsi < 30 ? 300 : 0, title = 'LONG', color = color.green)   

if is_uptrend
    watch_long := false
if is_downtrend
    watch_short := false
```