# Program for properly reading dopa's population census file
## Changing the extension from xls into html
folder_path <- "C:/Data/Population"
xls_files <- list.files(path=folder_path, pattern="\\.xls$", full.names=TRUE)
for (file in xls_files) {
    new_filename <- sub("\\.xls$", ".html", file)
    file.rename(file, new_filename)
}
print("All XLS files in the folder have been changing to HTML files.")

## Rewriting into csv files
library(rvest)
setwd(folder_path)
convert_html_to_csv <- function(filepath) {
    webpage <- read_html(filepath, encoding="UTF-8")
    data <- webpage %>% html_table(fill=TRUE) %>% as.data.frame
    if (!is.null(data)) {
        colnames(data) <- data[1, ]
        data <- data[-1, ]
        output_filename <- gsub(".html", ".txt", basename(filepath))
        write.table(data, paste0(dirname(filepath), "/", output_filename), na="", sep="|", row.names=FALSE)
        message(paste("Converted:", filepath, "to", output_filename, sep = " "))
    }
}

### Apply the function to all .html files recursively
list.files(folder_path, pattern=".html", recursive=TRUE) %>% sapply(convert_html_to_csv)
