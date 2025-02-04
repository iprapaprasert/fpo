let
    LatestDate = Date.StartOfMonth(Date.AddMonths(Date.From(DateTime.LocalNow()), -1)),
    ParameterTable = #table(
        {"StartDate", "EndDate"},
        {
            {#date(2010, 1, 1), #date(2020, 1, 1)},
            {#date(2020, 1, 1), LatestDate}
        }
    )
in
    ParameterTable
