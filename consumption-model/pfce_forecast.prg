' define
%path = "z:\databank\consumption\consumption.xlsx"

' import pfce
import(page=quarterly) %path range=pfce_r colhead=1 na="#N/A" @id @date(date) @smpl @all

' import bot_pci
import(page=monthly) %path range=bot_pc colhead=1 na="#N/A" @id @date(date) @smpl @all

' arima forecast bot_pce_idx
pageselect monthly
smpl @all if bot_pc_idx <> na
equation arma_pci.ls(optmethod=opg) dlog(bot_pc_idx) c ar(1 to 3) ar(11) sar(12) sma(12)
'' forecast bot_pce_idxf
pagestruct(end=2026M12) ' should be dynamic !
smpl @all if bot_pc_idx = na
arma_pci.forecast(e, g) bot_pc_idx_f
smpl @all

' forecast pfce
''' copy from monthly to quarterly
pageselect quarterly
pagestruct(end=2026Q4) ' should be dynamic !
smpl @all
copy(c=a) monthly\bot_pc_idx quarterly\bot_pc_idx
copy(c=a) monthly\bot_pc_idx_f quarterly\bot_pc_idx_f

pageselect quarterly
equation ls_pfce.ls @pcy(pfce_r) c @pcy(bot_pc_idx_f) @pcy(pfce_r(-1))
smpl @all if pfce_r = na
ls_pfce.forecast(e, g) pfce_r_f_ls
smpl @all

equation midas_pfce.midas(maxlag=9, lag=auto) @pcy(pfce_r) c @pcy(pfce_r(-1)) @  monthly\@pcy(bot_pc_idx_f)
smpl @all if pfce_r = na
midas_pfce.forecast(e, g) pfce_r_f_midas
smpl @all
show pfce_r pfce_r_f_ls pfce_r_f_midas
