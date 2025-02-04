' define
%path = "z:\databank\consumption\consumption.xlsx"
%sa_vars = "vat dom_vat imp_vat rvat dom_rvat imp_rvat sedan_new_reg moto_new_reg psg_car_sales"

' import sheet and create series
import(page=monthly) %path range=input colhead=1 na="#N/A" @id @date(date) @smpl @all

series vat = dom_vat + imp_vat
series imp_price_idx_2019 = imp_price_idx / @meansby(imp_price_idx, @crossid, "2019m01 2019m12") * 100

' generate real vat, based year 2019
series dom_rvat = dom_vat / headline_cpi * 100
series imp_rvat = imp_vat / imp_price_idx_2019 * 100
series rvat = dom_rvat + imp_rvat
' generate monthly seasonally adjusted x13
for %s {%sa_vars}
    {%s}.x13(save="d11")  @x11()
    %saname = %s + "_d11"
    %newname = @replace(%saname, "_d11", "_sa")
    rename {%saname} {%newname}  
next

' quarterly
pagecreate(page=quarterly) q
for %s {%sa_vars}
    copy(c=s) monthly\{%s} quarterly\{%s}
    pageselect quarterly
    {%s}.x13(save="d11")  @x11()
    %saname = %s + "_d11"
    %newname = @replace(%saname, "_d11", "_sa")
    rename {%saname} {%newname}
    pageselect monthly
next

' save results to excel
pageselect monthly
' alpha strdate = @datestr(@date, "YYYY-MM-DD")
wfsave(2, type=excelxml, na="", mode=update) %path range="monthly!b4" ' @keep strdate *

pageselect quarterly
'alpha strdate = @datestr(@date, "YYYY-MM-DD")
wfsave(2, type=excelxml, na="", mode=update) %path range="quarterly!b4" '@keep strdate *
