library(tidyverse)
library(magrittr)
library(xml2)
library(glue)
library(lubridate)

#Read in files
#Change these to location of the files on your own machine. 
#Use absolute paths for best results. 
complete_file_paths <- c(
  "tca_201908_child_child16_cci_video_glossed-flibl_through-2022_10_17-16_08.eaf",
  "tca_201907_child_child5_cci_video_glossed-flibl_through-2022_10_17-16_22.eaf",
  "tca_201908_child_child27_cci_video_glossed-flibl_through-2022_10_17-16_28.eaf"
)
#Alternatively, use list.files() over a directory containing all of your glossed EAFs.
#complete_file_paths <- list.files("/Users/path/to/glossed_eaf_directory")

#Requirements for ELAN files:
#-files must be Flibl output
#-tier names must begin with the participant code followed by a dash
##-e.g. Victoria-txt is good; Victoria_txt, txt-Victoria and txt@Victoria are bad
#-to read in target tiers, participant code must begin with 'Child' or 'CHI'

#Load EAF processing script
source("eaf_to_table_functions.R")

#Define the three-letter FLEx code for your study language
lang_code <- "" #Fill in FLEx code inside the quotes

#Read EAFs into table
eaf_tables_list <- vector(mode="list",length=length(complete_file_paths))
for (i in 1:length(eaf_tables_list)) {
  input <- complete_file_paths[i]
  recording_id <- input
  eaf <- read_xml(input)
  #Replace "tca" with the FLEx code for your study language
  eaf_tables_list[[i]] <- eaf_table(eaf,lang_code) %>%
    mutate(RecordingID=recording_id)
}
all_eafs_table <- bind_rows(eaf_tables_list)

#You now have two choices:

#Use all_eafs_table as is in the same R session

#Unnest all_eafs_table and write it to a CSV
#If you take this option, you should re-nest the word and morpheme columns to maintain tidy data structure
#when reading back into R.
all_eafs_table_flat <- all_eafs_table %>%
  unnest(WordData, keep_empty = TRUE) %>%
  unnest(MorphemeData, keep_empty = TRUE) %>%
  unnest(TargetWordData, keep_empty = TRUE) %>%
  unnest(TargetMorphemeData, keep_empty = TRUE)

write_csv(all_eafs_table_flat,"./combined_eafs_table.csv")

#Check that you can read this back in
reread <- read_csv("./combined_eafs_table.csv", na = c("NA"),
                   col_types = list(
                     WordText = "c",
                     TargetWordText = "c")) %>%
  nest(TargetMorphemeData=starts_with("TargetMorph")) %>%
  nest(TargetWordData=c(starts_with("TargetWord"),TargetMorphemeData)) %>%
  nest(MorphemeData=starts_with("Morph")) %>%
  nest(WordData=c(starts_with("Word"),MorphemeData)) %>%
  select(names(all_eafs_table))

#Running identical() returns FALSE but this is solely due to different treatment of NA vs. NULL in nest and unnest.