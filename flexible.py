# v12
from typing import List
from uuid import uuid4
import xml.etree.ElementTree as ET
import json
import re

config = json.load(open("to_flextext_config.json"))

# Using the definitions from the config file, make dict of language-charset pairs.
word_forming = {
    config["languages"]["main_language"]: re.compile("([^" + config["valid_characters"]["main_language"] + "])"),
    config["languages"]["child_language"]: re.compile("([^" + config["valid_characters"]["child_language"] + "])")
}

def tokenize(phrase: str, lg: str):
    """Tokenize an utterance based on specified word-forming characters.

    Parameters:
        phrase: the string to be tokenized
        lg: the language whose word-forming characters are to be used in tokenization
    
    Return list of tokens
    """
    if phrase:
        tokens = [j for j in [i.strip() for i in word_forming[lg].split(phrase)] if j]
        collected_tokens = []
        punct_chars = ""
        for token in tokens:
            if token == ".":
                punct_chars += token
            else:
                if punct_chars:
                    collected_tokens.append(" " + punct_chars)
                    punct_chars = ""
                collected_tokens.append(token)
        return collected_tokens
    else:
        return []

def print_el_info(el: ET.Element):
    """Print the tag, attributes, text, and number of children of an ET.Element
    
    Parameters:
        el: Element to be printed
    """
    print("\n","Tag:", el.tag, "\nAttrs:", str(el.attrib), "\nText:", el.text, "\nNo. of Children:", len(el))

def time_values(eaf_root: ET.Element):
    """Get time IDs and values from an EAF file
    
    Parameters:
        eaf_root: the root element of an EAF object parsed through ElementTree

    Return a dictionary of time ID and value pairs
    """
    return {i.attrib["TIME_SLOT_ID"]:i.attrib["TIME_VALUE"] \
        for i in eaf_root.findall(".//TIME_SLOT")
        }

def add_word_el(tokenized_utt: List[str], phrase_el: ET.Element, lg: str):
    """Populate a phrase element with a tokenized utterance
    
    Parameters:
        tokenized_utt: a list with tokens from an utterance
        phrase_el: the element that will be the parent to the words added (below the words el in the phrase_el will be the items w/ translations and notes)
        lg: the language whose word-forming characters are to be used in tokenization
    
    Makes changes in place (returns nothing)
    """
    words = ET.Element("words")
    utterance_word_forming = word_forming[lg]
    for token in tokenized_utt:
        word = ET.Element("word", attrib={"guid":str(uuid4())})
        if utterance_word_forming.search(token):
            type = "punct"
        else:
            type = "txt"
        token_el = ET.Element("item", attrib={"type": type, "lang": lg})

        token_el.text = token
        word.append(token_el)
        words.append(word)
    phrase_el.append(words)

def remove_constraint(constraint: str, eaf: ET.Element):
    """Remove the tiers that use the "Included In" stereotype constraint

    Parameters:
        eaf: The root element of an EAF file
    
    Makes changes in place (returns nothing)    
    """
    for constraint_tier in eaf.findall(".//*[@CONSTRAINTS='{}']".format(constraint)):
        for bad_tier in eaf.findall(".//*[@LINGUISTIC_TYPE_REF='{}']".format(constraint_tier.attrib["LINGUISTIC_TYPE_ID"])):
            eaf.remove(bad_tier)

def make_times(flextext: ET.Element):
    """Make the TIME_ORDER element for the output EAF

    Parameters:
        flextext: the root of the parsed flextext exported from FLEx

    Returns an ET.Element of TIME_ORDER
    """
    phrases = flextext.findall(".//*phrase")
    time_order = ET.Element("TIME_ORDER")
    tsN = 1
    for i in phrases:
        try:
            begin = ET.Element("TIME_SLOT", attrib={"TIME_SLOT_ID":"ts"+str(tsN), "TIME_VALUE":i.attrib["begin-time-offset"]})
            end = ET.Element("TIME_SLOT", attrib={"TIME_SLOT_ID":"ts"+str(tsN+1), "TIME_VALUE":i.attrib["end-time-offset"]})
            tsN += 2
            time_order.append(begin)
            time_order.append(end)
        except:
            next
    return time_order
            
def make_assoc_annotation(base_tier_name: str, tier_type: str, content_dict: dict, parent_aID: str, aID_count: int, eaf: ET.ElementTree):
    """Make an annotation of the type Symbolic Association
    
    Parameters:
        base_tier_name: the prefix for the tiers to be made; will include at minimum the speaker code
        tier_type: the type of tier in ELAN, defined by the kind of content in it, such as morphological gloss or translation
        content_dict: the dict of items to be read from, where the content of the annotation will be. This will either be a dict containing information of a phrase, a word, or a morph
        content_aID: the aID of the parent element to the one being created
        aID_count: the present aID in the count as we create more annotations
    
    Returns next aID to be used in the creation of the EAF; makes changes to EAF XML document tree in place
    """
    # tier_content_type is -pos etc
    # phrase_word_morph_dict is var word or var phase in the original constr script, which is just where i slice the string and give each word a dict of info like pos, morphs etc or where the xds, notes etc are stored in the case of phrase dict
    # basline_word_aID is the baseline aID or word aID, depending on if this is for the phrase level or word level ref ann
    # i'll want to run this with like 
    # for note_type in ["pos", "xds", ...]:
        # make_assoc_annotation(base_tier_name, note_type, eaf, word, word_aID)
    x_aID = aID_count
    aID_count += 1
    x_tier_name = base_tier_name + "-" + tier_type
    x_tier = eaf.find(".//TIER[@TIER_ID='{}']".format(x_tier_name))
    new_x_ann = ET.Element("REF_ANNOTATION", attrib={"ANNOTATION_ID":"a"+str(x_aID), "ANNOTATION_REF":parent_aID})
    new_x_ann_val = ET.Element("ANNOTATION_VALUE")
    try:
        new_x_ann_val.text = content_dict[tier_type]
    except KeyError:
        print("It's possible you didn't export the flextext with all of the fields visible.")
        raise
        
    new_x_ann.append(new_x_ann_val)
    x_ann = ET.Element("ANNOTATION")
    x_ann.append(new_x_ann)
    x_tier.append(x_ann)

    return aID_count