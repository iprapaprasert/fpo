let
    // If the code goes error, "Formula.Firewall: Query references other queries, so it may not directly access a data source."
    // Go to Data tab -> expand Get Data -> Query Options -> Privacy -> Always ignore Privacy Level settings -> OK

    // Define the API base URL
    BaseURL = "https://apigw1.bot.or.th/bot/public/observations/",

    // Input Arguments
    CrossJoin = Table.AddColumn(
        Table.FromList(
            List.Distinct(BotPciValmap[SeriesCode]), 
            Splitter.SplitByNothing(),
            {"SeriesCode"}
        ),
        "Dates", 
        each bot_pc_parameter
    ),
    InputTable = Table.ExpandTableColumn(CrossJoin, "Dates", {"StartDate", "EndDate"}),

    // Function to fetch data for each series code
    FetchData = (Series as text, StartDate as date, EndDate as date) =>
        let
            // Convert StartDate and EndDate to text format for API
            StartDateText = Text.From(Date.ToText(StartDate, "yyyy-MM-dd")),
            EndDateText = Text.From(Date.ToText(EndDate, "yyyy-MM-dd")),
            
            // Build the full API URL with parameters
            FullURL = BaseURL & "?series_code=" & Series & "&start_period=" & StartDateText & "&end_period=" & EndDateText & "&sort_by=asc", 

            // Make the API call
            Source = Json.Document(
                Web.Contents(
                    FullURL,
                    [Headers=[Accept="application/json", #"x-ibm-client-id"="d2ee985e-51c5-4e56-81b3-0bd5dc983e02"]] 
                )
            ),

            // Navigate to the data table
            Observations = Source[result][series]{0}[observations],

            // Convert to table
            Table = Table.FromList(Observations, Splitter.SplitByNothing(), null, null, ExtraValues.Error),

            // Expand the records
            ExpandedTable = Table.ExpandRecordColumn(Table, "Column1", {"period_start", "value"}),

            // Rename columns, transform date column and add series code
            RenamedTable = Table.RenameColumns(ExpandedTable, {{"period_start", "Date"}, {"value", "Value"}}),
            DateTransformedTable = Table.TransformColumns(RenamedTable, {{"Date", each Date.From(Text.From(_) & "-01"), type date}}),
            FinalTable = Table.AddColumn(DateTransformedTable, "SeriesCode", each Series)
        in
            FinalTable,

    // Fetch data for all series codes and combine
    AllData = List.Transform(Table.ToRecords(InputTable), each FetchData(_[SeriesCode], _[StartDate], _[EndDate])),
    CombinedTable = Table.Combine(AllData),

    // Merge CombinedTable with BotPciValMap to get the Variable (Series Name)
    MergedTable = Table.NestedJoin(CombinedTable, "SeriesCode", BotPciValmap, "SeriesCode", "SeriesDetail", JoinKind.LeftOuter),

    // Expand the merged table to include the Variable column (Series Name)
    ExpandedTable = Table.ExpandTableColumn(MergedTable, "SeriesDetail", {"Indicator"}),

    // Pivot table
    RemovedColumn = Table.RemoveColumns(ExpandedTable, {"SeriesCode"}),
    PivotedColumn = Table.Pivot(RemovedColumn, List.Distinct(RemovedColumn[Indicator]), "Indicator", "Value"),
    ChangedType = Table.TransformColumnTypes(PivotedColumn, {{"bot_pc_idx", type number}, {"bot_ndr_idx", type number}, {"bot_gasoline_idx", type number}, {"bot_elec_idx", type number}, {"bot_semdr_idx", type number}, {"bot_semdr_sales_idx", type number}, {"bot_tex_imp_idx", type number}, {"bot_dr_idx", type number}, {"bot_comm_car", type number}, {"bot_psg_car", type number}, {"bot_motorcycle", type number}, {"bot_serv_idx", type number}, {"bot_transport_idx", type number}, {"bot_hotel_rest_idx", type number}, {"bot_non_res_exp_idx", type number}, {"bot_pc_idx_sa", type number}, {"bot_ndr_idx_sa", type number}, {"bot_gasoline_idx_sa", type number}, {"bot_elec_idx_sa", type number}, {"bot_semdr_idx_sa", type number}, {"bot_semdr_sales_idx_sa", type number}, {"bot_tex_imp_idx_sa", type number}, {"bot_dr_idx_sa", type number}, {"bot_comm_car_sa", type number}, {"bot_psg_car_sa", type number}, {"bot_motorcycle_sa", type number}, {"bot_serv_idx_sa", type number}, {"bot_transport_idx_sa", type number}, {"bot_hotel_rest_idx_sa", type number}, {"bot_non_res_exp_idx_sa", type number}})
in
    ChangedType
