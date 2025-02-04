library("tidyverse")
library("haven")

folder_path <- "//tsclient/O/+Regional Economy+/สำนักงานสถิติ/Microdata/11 LFS/LFS/LFS 2559 (2016)"
file_ext <- ".sav"
setwd(folder_path)

convert_sav_to_csv <- function(filepath) {
    data <- read_sav(filepath)
    if (!is.null(data)) {
        output_filename <- gsub(file_ext, ".csv", basename(filepath))
        write.csv(data, paste0(dirname(filepath), "/", output_filename), na="", row.names=FALSE)
        message(paste("Converted:", filepath, "to", output_filename, sep = " "))
    }
}

# Apply the function to all .sav files recursively
list.files(folder_path, pattern=file_ext, recursive=TRUE) %>%
    sapply(convert_sav_to_csv)
