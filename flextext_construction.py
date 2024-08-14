# v04.7
import xml.etree.ElementTree as ET
import flexible as flibl
import re
from datetime import datetime
import json
from uuid import uuid4

# Open the config file and define relevant variables
config = json.load(open("to_flextext_config.json"))
for name in config["file_names"]:
    file_name = name
    language = config["languages"]["main_language"]
    flex_language = config["languages"]["flex_language"]

    # if you have target utterances and use a different language in FLEx for the phonetic renderings of those in FLEx, give that language code here
    child_language = config["languages"]["child_language"]

    # Open and parse the EAF
    eaf_parsed = ET.parse(file_name)
    eaf_root = eaf_parsed.getroot()
    media_guid = str(uuid4())

    # Create XML tree for the FLExText
    document = ET.ElementTree(ET.Element("document"))
    document_root = document.getroot()
    interlinear_text = ET.Element("interlinear-text", attrib={"guid":str(uuid4())})

    # Generate the title
    title = ET.Element("item", attrib={"type":"title", "lang":flex_language})
    # Truncate the path to be just the file name without the extension
    eaf_split_pattern = re.compile("[^/]+\\.eaf")
    title_match = eaf_split_pattern.search(file_name)[0][:-4]
    title.text = title_match
    # Right now, being in beta, we are titling the text and naming the file using the date and time of creation, so you can keep track of different versions in case things go awry and you have to delete something.
    now = str(datetime.now()).split(" ")
    time = now[1].split(":")
    date_time = now[0].replace("-", "_") + "-{}_{}".format(time[0], time[1])
    title.text += "-" + date_time

    interlinear_text.append(title)

    paragraphs = ET.Element("paragraphs")

    # Remove the tiers by constraint, if specified
    for i in config["exclude_tier_constraint"]:
        flibl.remove_constraint(i, eaf_root)

    # Get dict of time IDs and their values
    times = flibl.time_values(eaf_root)

    # Special tiers to consider
    exclude_ids = config["exclude_tier_id"]
    exclude_types = config["exclude_tier_type"]
    translation_tiers = config["translation_tiers"]
    # Make a flat list of all the tier IDs associated with each of the target utterance tier types
    target_tiers = [i.attrib["TIER_ID"] for j in config["target_utterance_tier_type"] for i in eaf_root.findall(".//*[@LINGUISTIC_TYPE_REF='{}']".format(j))]
    
    # Make tier groups
    top_tiers = []
    # Populate the top-level tiers
    for i in eaf_root.findall("TIER"):
        if ("PARENT_REF" not in i.attrib.keys()) and (i.attrib["TIER_ID"] not in exclude_ids) and (i.attrib["LINGUISTIC_TYPE_REF"] not in exclude_types):
            top_tiers.append({
                "PARENT_TIER_ID": i.attrib["TIER_ID"],
                "PARTICIPANT": i.attrib["PARTICIPANT"],
                "PARENT_TIER": i,
                "CHILD_TIERS": []
            })

    # Populate the child tiers
    for i in eaf_root.findall("TIER"):
        # Only put the tier in if it's meant to be included
        if ("PARENT_REF" in i.attrib.keys()) and (i.attrib["LINGUISTIC_TYPE_REF"] not in exclude_types)and (i.attrib["TIER_ID"] not in exclude_ids):
            for j in top_tiers:
                # Place the child tier under the appropriate parent tier (i.e. if the parent of a tier matches the ID of another tier, place the first tier under the parent)
                if j["PARENT_TIER_ID"] == i.attrib["PARENT_REF"]:
                    j["CHILD_TIERS"].append(i)
                    break

    # Make annotations dict: keys = annotaion IDs from ELAN, values = dicts with guid, begin-time-offset, end-time-offset, text, speaker, media-file, CHILD_TIERS
    annotations = {}
    for alignable_tier in top_tiers:
        for annotation in alignable_tier["PARENT_TIER"]:
            # Assign attributes for each annotation
            annotation_id = annotation[0].attrib["ANNOTATION_ID"]
            annotation_content = {}
            annotation_content["guid"] = str(uuid4())
            annotation_content["begin-time-offset"] = times[annotation[0].attrib["TIME_SLOT_REF1"]]
            annotation_content["end-time-offset"] = times[annotation[0].attrib["TIME_SLOT_REF2"]]
            annotation_content["text"] = annotation[0][0].text
            annotation_content["speaker"] = alignable_tier["PARTICIPANT"]
            annotation_content["media-file"] = media_guid
            annotation_content["CHILD_TIERS"] = {}
            annotations[annotation_id] = annotation_content
        # Get the note/translations into the CHILD_TIERS--these won't be tokenized, rather placed as full strings at the phrase level, in "Notes" in FLEx
        for reference_tier in alignable_tier["CHILD_TIERS"]:
            for annotation in reference_tier:
                this_annotation_id = annotation[0].attrib["ANNOTATION_REF"]
                if reference_tier.attrib["TIER_ID"] in translation_tiers.keys():
                    annotation[0][0].attrib["translation"] = translation_tiers[reference_tier.attrib["TIER_ID"]]
                else:
                    annotation[0][0].attrib["translation"] = ""
                annotations[this_annotation_id]["CHILD_TIERS"][reference_tier.attrib["TIER_ID"]] = annotation[0][0]

    # Fill in the main content
    for annotation in annotations:
        # Initialize the annotation as not having an associated target utterance
        target = False
        annotation_dict = annotations[annotation]
        aID = annotation
        # Make elements for the internal elements per utterance
        paragraph = ET.Element("paragraph", attrib={"guid": str(uuid4())})
        phrases = ET.Element("phrases")
        phrase = ET.Element("phrase", attrib={"guid":str(uuid4()), "begin-time-offset": annotation_dict["begin-time-offset"], "end-time-offset": annotation_dict["end-time-offset"], "speaker": annotation_dict["speaker"], "media-file": annotation_dict["media-file"]})
        # A list of Note elements for FLEx, to be populated
        notes = []
        # Add all the Note elements
        for i in annotation_dict["CHILD_TIERS"]:
            # If the child tier is a translation, make a special translation (gls) element for it
            if annotation_dict["CHILD_TIERS"][i].attrib["translation"]:
                note = ET.Element("item", attrib={"type":"gls", "lang":annotation_dict["CHILD_TIERS"][i].attrib["translation"]})
            # If there is an associated target tier, mark the variable target as such, so it can be added later
            elif i in target_tiers:
                target = True
                target_text = annotation_dict["CHILD_TIERS"][i].text
                continue
            # Otherwise, consider it a note
            else:
                note = ET.Element("item", attrib={"type":"note", "lang":flex_language})
            # Fill the note/gls element with the text of the annotation
            note.text = annotation_dict["CHILD_TIERS"][i].text
            notes.append(note)
        # Add the notes needed to indicate metadata
        phonetic_note = ET.Element("item", attrib={"type":"note", "lang":flex_language})
        if target:
            phonetic_note.text = "Target"
        else:
            phonetic_note.text = "Phonetic"
        notes.append(phonetic_note)
        id_note = ET.Element("item", attrib={"type":"note", "lang":flex_language})
        id_note.text = aID
        notes.append(id_note)
        speaker_note = ET.Element("item", attrib={"type":"note", "lang":flex_language})
        speaker_note.text = annotation_dict["speaker"]
        notes.append(speaker_note)
        # If there is an associated target utterance, use the original utterance as child language and the target as the main language
        if target:
            # Use the defined child_language to tokenize the original utterance
            text = flibl.tokenize(annotation_dict["text"], child_language)
            flibl.add_word_el(text, phrase, child_language)
            # Add the notes, similarly to how it was done above
            for i in notes:
                phrase.append(i)
            phrases.append(phrase)
            paragraph.append(phrases)
            paragraphs.append(paragraph)
            target_phrase = ET.Element("phrase", attrib={"guid":str(uuid4()), "begin-time-offset": annotation_dict["begin-time-offset"], "end-time-offset": annotation_dict["end-time-offset"], "speaker": annotation_dict["speaker"], "media-file": annotation_dict["media-file"]})
            # Use the defined language (i.e. the general Vernacular as defined by FLEx) to tokenize the target utterance
            text = flibl.tokenize(target_text, language)
            flibl.add_word_el(text, target_phrase, language)
            # Add notes as above, but only to give the ID and the fact that this is the target utterance
            target_phrase.append(id_note)
            target_note = ET.Element("item", attrib={"type":"note", "lang":flex_language})
            target_note.text = "Target"
            target_phrase.append(target_note)
            target_paragraph = ET.Element("paragraph", attrib={"guid": str(uuid4())})
            target_phrases = ET.Element("phrases")
            target_phrases.append(target_phrase)
            target_paragraph.append(target_phrases)
            paragraphs.append(target_paragraph)
        # If there isn't an associated target utterance, just use the main language
        else:
            text = flibl.tokenize(annotation_dict["text"], language)
            flibl.add_word_el(text, phrase, language)
            # Add all appropriate notes to utterance
            for i in notes:
                phrase.append(i)
            phrases.append(phrase)
            paragraph.append(phrases)
            paragraphs.append(paragraph)

    # FLEx wants a number for each phrase, that's seg_count
    seg_count = 1
    seg_num_paras = []
    # Go through the paragraphs sorted by the begin-time-offset (i.e. their starting time), and add a segnum element to each
    # Populate seg_num_paras with the paragraphs, correctly ordered, with the segnum element
    for para in sorted(paragraphs, key=lambda para: int(para[0][0].attrib["begin-time-offset"])):
        segnum = ET.Element("item", attrib={"type":"segnum", "lang":flex_language})
        segnum.text = str(seg_count)
        seg_count += 1
        para[0][0].insert(0, segnum)
        seg_num_paras.append(para)
    
    # Generate a paragraphs element with all of the paragraphs, in order as defined just above
    new_paragraphs = ET.Element("paragraphs")
    for i in seg_num_paras:
        new_paragraphs.append(i)
    # Add the paragraphs to the flextext document
    interlinear_text.append(new_paragraphs)

    # Defining languages for FLEx
    language_defs = config["language_fonts"]
    languages = ET.Element("languages")
    for i in language_defs:
        languages.append(ET.Element("language", attrib=i))
    # Add the langauge definitions to the flextext document
    interlinear_text.append(languages)

    # Media metadata
    media_descriptor = eaf_root.findall(".//MEDIA_DESCRIPTOR") # taking the first 
    media_files = ET.Element("media-files", attrib={"offset-type": ""})
    media = ET.Element("media", attrib={"guid":media_guid, "location": media_descriptor[0].attrib["MEDIA_URL"]})
    media_files.append(media)
    # Make media elements for the flextext
    for i in media_descriptor[1:]:
        secondary_media = ET.Element("media", attrib={"guid":str(uuid4()), "location": i.attrib["MEDIA_URL"]})
        media_files.append(secondary_media)
    # Add the media descriptors to the flextext document
    interlinear_text.append(media_files)

    # Finalize everything by writing it to the flextext document
    document_root.append(interlinear_text)

    # Write the file
    ET.indent(document, space="\t", level=0)
    document.write("{}-elan_export-{}.flextext".format(file_name[:-4], date_time))
