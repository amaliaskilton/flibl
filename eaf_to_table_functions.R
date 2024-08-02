#Functions needed for the code to run
library(tidyverse)
library(magrittr)
library(xml2)
library(glue)

#get_own_aid takes an XML node that is an ELAN annotation, gets AID of the annotation
#get_ref_aid gets AID that is listed as the referring annotation
get_own_aid = function(eaf_node) {xml_attr(eaf_node,"ANNOTATION_ID")}
get_ref_aid = function(eaf_node) {xml_attr(eaf_node,"ANNOTATION_REF")}

#get_timestamp takes TSRs of a time-aligned annotation and replaces them with actual timestamps in SS.ms format
get_timestamp = function(eaf,tsr){
  tsr_path <- glue(".//TIME_ORDER/TIME_SLOT[@TIME_SLOT_ID='{tsr}']")
  return(as.numeric(xml_find_first(eaf,tsr_path) %>% xml_attr("TIME_VALUE"))/1000)
}

#find_participants finds all participant codes in an EAF where tiers are named in the format participant_code-xx-yy
find_participants = function(eaf) {
  participants <- tibble(prefix=(xml_find_all(eaf,".//TIER") %>% 
                                   xml_attr("TIER_ID") %>% 
                                   str_extract("^[[:alnum:]]*(?=-)") %>% 
                                   unique())) %>%
    filter(!is.na(prefix)) %>%
    mutate(speaker_type="adult") %>%
    mutate(speaker_type=ifelse(str_detect(prefix,"CHI") | str_detect(prefix,"Child[[:digit:]]*$"),"child","adult"))
  return(participants)
}

#single_participant_table takes EAF, participant code, lang code, and speaker type
#Then creates a table of all tiers, hierarchically organized, for that participant
single_participant_table = function(eaf, tier_prefix, lang_code, speaker_type) {
  #Define expected tiers
  tiers = tibble(
    tiertypes = c(
      "phonetic",
      "xds",
      "phonetic-words",
      "phonetic-pos",
      "phonetic-morph-txt",
      "phonetic-morph-cf",
      "phonetic-morph-gls",
      "phonetic-morph-msa"
    )
  )
  if (speaker_type == "child") {
    target_tiertypes = tiers %>% mutate(tiertypes = str_replace_all(tiertypes, "phonetic", "target"))
    tiers = bind_rows(tiers, target_tiertypes) %>% distinct()
  }
  tiers = tiers %>%
    mutate(tiernames = ifelse(
      tiertypes == "xds",
      glue("{tier_prefix}-{tiertypes}"),
      glue("{tier_prefix}-{lang_code}-{tiertypes}")
    )) %>%
    mutate(tierpaths = ifelse(
      tiertypes == "phonetic",
      glue(
        ".//TIER[@TIER_ID='{tiernames}']/ANNOTATION/ALIGNABLE_ANNOTATION"
      ),
      glue(
        ".//TIER[@TIER_ID='{tiernames}']/ANNOTATION/REF_ANNOTATION"
      )
    ))
  
  #Find all annotations on each tier
  tiernodes = vector(mode = "list", length = nrow(tiers))
  for (i in 1:length(tiernodes)) {
    tiernodes[[i]] = xml_find_all(eaf, tiers$tierpaths[i])
  }
  
  #From each nodeset, create tibble with text, own AID, and if applicable referring AID.
  tiertibbles = vector(mode = "list", length = length(tiernodes))
  for (i in 1:length(tiertibbles)) {
    ifelse(
      tiers$tiertypes[i] == "phonetic",
      tiertibbles[[i]] <-
        tibble(
          Turn = xml_text(tiernodes[[1]]),
          PhraseAID = get_own_aid(tiernodes[[1]]),
          BeginTime = get_timestamp(eaf, xml_attr(tiernodes[[1]], "TIME_SLOT_REF1")),
          EndTime = get_timestamp(eaf, xml_attr(tiernodes[[1]], "TIME_SLOT_REF2"))
        ),
      tiertibbles[[i]] <-
        tibble(
          Text = xml_text(tiernodes[[i]]),
          OwnAID = get_own_aid(tiernodes[[i]]),
          RefAID = get_ref_aid(tiernodes[[i]])
        )
    )
  }
  
  #Name the tibbles according to their tier types.
  names(tiertibbles) <- str_replace_all(tiers$tiertypes, "-", "_")
  
  #Make sure every tibble column has a unique name.
  for (i in 2:length(tiertibbles)) {
    tibblename = names(tiertibbles)[i]
    names(tiertibbles[[i]]) = paste(tibblename, names(tiertibbles[[i]]), sep =
                                      "_")
  }
  
  #Join all morpheme info
  morphemes <- left_join(
    tiertibbles[["phonetic_morph_txt"]],
    tiertibbles[["phonetic_morph_cf"]],
    by = c("phonetic_morph_txt_OwnAID" = "phonetic_morph_cf_RefAID")
  ) %>%
    left_join(tiertibbles[["phonetic_morph_gls"]],
              by = c("phonetic_morph_txt_OwnAID" = "phonetic_morph_gls_RefAID")) %>%
    left_join(tiertibbles[["phonetic_morph_msa"]],
              by = c("phonetic_morph_txt_OwnAID" = "phonetic_morph_msa_RefAID"))
  
  names(morphemes) <- c(
    "Morpheme",
    "MorphemeAID",
    "WordAID",
    "MorphemeUR",
    "MorphemeURAID",
    "MorphemeGls",
    "MorphemeGlsAID",
    "MorphType",
    "MorphTypeAID"
  )
  
  #Also join word info
  words <- left_join(tiertibbles[["phonetic_words"]],
                     tiertibbles[["phonetic_pos"]],
                     by = c("phonetic_words_OwnAID" = "phonetic_pos_RefAID"))
  
  names(words) <-
    c("WordText", "WordAID", "PhraseAID", "WordPOS", "WordPOSAID")
  
  #Join morphemes to words
  #To keep data tidy, nest the morpheme info
  morphemes_words <- morphemes %>%
    nest(
      data = c(
        Morpheme,
        MorphemeAID,
        MorphemeUR,
        MorphemeURAID,
        MorphemeGls,
        MorphemeGlsAID,
        MorphType,
        MorphTypeAID
      )
    ) %>%
    rename(MorphemeData = data) %>%
    left_join(words, by = "WordAID")
  
  #Get phrases tables
  phrases <- tiertibbles[["phonetic"]]
  xds <-
    tiertibbles[["xds"]] %>% rename(XDS = xds_Text,
                                XDS_AID = xds_OwnAID,
                                PhraseAID = xds_RefAID)
  phrases <- left_join(phrases, xds, by = "PhraseAID")
  
  #Now join words to phrases
  all <- left_join(phrases, morphemes_words, by = "PhraseAID") %>%
    nest(WordData = c(WordText, WordAID, WordPOS, WordPOSAID, MorphemeData)) %>%
    mutate(Participant = tier_prefix)
  
  #If speaker has target tiers, do all this again for target tiers.
  if(sum(str_detect(names(tiertibbles),"target")) > 1) {
    #Join all target morpheme info.
    target_morphemes <- left_join(
      tiertibbles[["target_morph_txt"]],
      tiertibbles[["target_morph_cf"]],
      by = c("target_morph_txt_OwnAID" = "target_morph_cf_RefAID")
    ) %>%
      left_join(tiertibbles[["target_morph_gls"]],
                by = c("target_morph_txt_OwnAID" = "target_morph_gls_RefAID")) %>%
      left_join(tiertibbles[["target_morph_msa"]],
                by = c("target_morph_txt_OwnAID" = "target_morph_msa_RefAID"))
    
    names(target_morphemes) <- c(
      "TargetMorpheme",
      "TargetMorphemeAID",
      "TargetWordAID",
      "TargetMorphemeUR",
      "TargetMorphemeURAID",
      "TargetMorphemeGls",
      "TargetMorphemeGlsAID",
      "TargetMorphType",
      "TargetMorphTypeAID"
    )
    
    #Also join target word info.
    target_words <- left_join(tiertibbles[["target_words"]],
                              tiertibbles[["target_pos"]],
                              by = c("target_words_OwnAID" = "target_pos_RefAID"))
    
    names(target_words) <-
      c("TargetWordText", "TargetWordAID", "TargetPhraseAID", "TargetWordPOS", "TargetWordPOSAID")
    
    #Join target morphemes to target words
    #To keep data tidy, nest the morpheme info
    target_morphemes_words <- target_morphemes %>%
      nest(
        data = c(
          TargetMorpheme,
          TargetMorphemeAID,
          TargetMorphemeUR,
          TargetMorphemeURAID,
          TargetMorphemeGls,
          TargetMorphemeGlsAID,
          TargetMorphType,
          TargetMorphTypeAID
        )
      ) %>%
      rename(TargetMorphemeData = data) %>%
      left_join(target_words, by = "TargetWordAID")
    
    #Get target phrases table
    target_phrases <- tiertibbles[["target"]] %>%
    #Update names
      rename(TargetTurn=target_Text,TargetPhraseAID=target_OwnAID,PhraseAID=target_RefAID)
    
    #Join target words to target phrases
    target_words_phrases <- left_join(target_phrases, target_morphemes_words, by = "TargetPhraseAID") %>%
      nest(TargetWordData = c(TargetWordText, TargetWordAID, TargetWordPOS, TargetWordPOSAID, TargetMorphemeData))
    
    #Join target phrases to phonetic phrases
    all <- left_join(all,target_words_phrases,by="PhraseAID")
  }
  
  return(all)
}
  
#eaf_table creates a single table for all participants in a file
eaf_table = function(eaf,lang_code){
  participants <- find_participants(eaf)
  
  participant_tibbles <- vector(mode = "list",length=nrow(participants))
  
  for (i in 1:length(participant_tibbles)) {
    participant_tibbles[[i]] = single_participant_table(eaf=eaf,
                                                        tier_prefix=as.character(participants[i,"prefix"]),
                                                        lang_code = lang_code,
                                                        speaker_type=as.character(participants[i,"speaker_type"])
    )
  }
  
  all_participants_table <- bind_rows(participant_tibbles) %>%
    arrange(PhraseAID)
  
  return(all_participants_table)
}
