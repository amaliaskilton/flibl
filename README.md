Flibl is a tool to bolster the transfer of texts between ELAN and FLEx (and FLEx and ELAN). It runs as a set of python scripts with a configuration file that specifies user settings. Flibl converts files from ELAN to FLEx (and vice versa) through a JSON-like interchange format. The process, rationale, and background are described in a paper under review.

# Requirements
* Python 3.10.x+
    * Many computers come with Python installed. If you don't have Python, you can install it in many ways. We suggest using Miniconda (https://docs.anaconda.com/miniconda/miniconda-install/).
    * There are no extra dependencies that aren't already downloaded with Python
* FieldWorks Language Explorer (FLEx)
    * [Download free from SIL here](https://software.sil.org/fieldworks/download/)
* Active FLEx project
    * Your FLEx project must have writing systems set up for your language(s) of study and metalanguages. See the section below on writing system setup.
    * Your FLEx project does *not* need to have a lexicon or other interlinearized texts set up for your first import.
* Files from this repository, with the `.json` files edited to match your settings 
    * `flexible.py`
    * `to_flextext_config.json`
    * `flextext_construction.py`
    * `to_eaf_config.json`
    * `eaf_construction.py`
* Your own transcription files
    * An EAF file (if going from ELAN to FLEx)
    * A *morphologically parsed* FLExText file (if going from FLEx to ELAN)

# Warnings
* When setting up the config files, make sure to use quotation marks around all of the strings you type.
    * Exception: Do not quote `0` or `1` for the `"kid"` parameter in `to_eaf_config.json`
* Ensure you're using the right version of Python by typing `python --version` into your terminal/command prompt. If it returns something beginning with `2.`, try running `python3 --version`. 
    *  If either of those commands return something below `3.10`, please download a more recent version of Python [from their website](https://www.python.org/) and run Flibl using that. 
    *  If `python --version` gives you something above `3.0` but below `3.10` and `python3 --version` gives you an error of some kind, you still need to download something more recent.
* When glossing an imported FLExText in FLEx:
    * *Do not edit any of the note fields created by Flibl* (annotation number, speaker code, phonetic/target code, or addressee/XDS code). Editing other note fields is fine.
    * *Do not change any line breaks.*
    * Editing Flibl's notes or changing line breaks will break the FLEx to ELAN export.
* When exporting your FLExText after glossing, make sure that all fields are visible in the Texts module before you interactively export. This will ensure that you are exporting all of the information from the morphologically parsed text. Flibl includes as much as possible, so the user can decide what to exclude after exporting to ELAN.
* In the language list, `child_language` should be set to the same ISO code as `main_language`.
*  In a file with no child language, the following points are also important
  * No additional language beyond what's actually in the file should be included in the `language_fonts` list
  * For the `valid_characters` list the same list of characters should be repeated for the `child_language` 
  * The `target utterance tier type` should be blank
 

# Opening Configuration Files
Using Flibl will involve opening configuration files in a text editor, such as gedit, textedit, or notepad. If you want something fancier, people often opt for something like [VSCode](https://code.visualstudio.com/), but it's not necessary. Do not edit the files in Word, as that will likely introduce problems that cause them to not run (e.g. smart quotes, saving in a different format). You will also need to run the scripts in Python, which involves opening a Terminal/Console window and typing `python ` or `python3 ` and then the name of the script (e.g. `python flexible.py`).

# ELAN File Format
Flibl expects your input ELAN file to have the following characteristics. 

1. Transcription tier: The EAF must contain at least one time-aligned transcription tier. All transcription tiers which you want to analyze should have the same linguistic type. In earlier versions of ELAN, this was labeled the Time-Aligned stereotype. In later versions, the parent tiers have "none" as the stereotype but there is a check-box to mark them as "time-aligned".
2. Symbolic Association tiers: All tiers besides the time-aligned tier should belong to types with the Symbolic Association stereotype. Tiers with the same kind of data (e.g. translations, notes, target utterances) should have the same type. The transcription tier should be the parent of all of the Symbolic Association tiers.
3. All tiers: All tiers should have a participant attribute in the Tiers dialog. The participant attribute should be repeated as the first element of the tier name. 

You can check tier and type attributes in the Tier and Type menus. 

The [sample ELAN file](/example_eaf/YDN_202001_a_1.1_redacted.eaf) in this documentation can be used as a template for formatting your ELAN file. When converting files previously created, it is easy to overlook these steps. We recommend making an ELAN template that conforms to these specifications.

As of August, 2024, we are running into issues with non-ASCII characters and conversions across different platforms. We are actively working on this issue. 

### What if you have the translations in time-aligned tiers?

Especially if you created your ELAN file by importing a Praat TextGrid, you may have the translation, notes, etc. annotations in time-aligned tiers with the same timepoints as the transcription, rather than Symbolic Association tiers. 

It isn't possible to change a tier from time-aligned to Symbolic Association in ELAN. Instead, in this situation you should create new (blank) Symbolic Association tiers and copy the annotations into them using the "Tools > Copy Annotations from Tier to Tier" command in ELAN.

### What if you have a time-aligned gesture tier?

You might have other annotations, for example with gesture, gaze, or activity type information, that are time-aligned but have different timepoints than the transcription annotations. There are several ways to deal with this. 

1. Exclude Tiers - If you don't need to see the multimodal annotations while you analyze in FLEx, you can exclude them from the ELAN to FLEx import using the 'exclude tier types' or 'exclude tier IDs' fields in the config file. After you export back from FLEx to ELAN, you can merge the excluded tiers back into the file using the 'Merge transcriptions' command in ELAN.

2. Copy Annotations to a Symbolic Association Tier - This is likely the best option if you want to see the multimodal annotations while you analyze the text in FLEx, but you don't want to parse them like the speech/transcription. Create a blank Symbolic Association tier for each participant and use the "Copy Annotations from Tier to Tier" command in ELAN to copy the text of the overlapping multimodal annotations into it. However, you will not be able to copy/view any annotations that don't overlap with speech.

3. Change the Participant Attribute and Type - This is the best option if you want to parse the multimodal annotations along with the speech (e.g. you're analyzing simultaneous communication in a spoken and signed language). Change the linguistic type of your multimodal tiers to be the same as the type of your transcription tiers. Then, change the participant attribute of the multimodal tiers to include both the participant label and the original type label. 

For example, suppose you have the following time-aligned tiers:

| Tier Name | Type | Participant |
| --- | -- | --- | 
| LVI-gesture | gesture | LVI |
| LVI-transcription | transcription | LVI |

You would change them to:

| Tier Name | Type | Participant |
| --- | -- | --- | 
| LVI-gesture | transcription | LVI-gesture |
| LVI-transcription | transcription | LVI |

You will likely want to change the tier types and participant attributes back after you export back to ELAN.

# Exporting from ELAN to FLEx
When you have an ELAN text that has been annotated to your satisfaction and is ready to go into FLEx, you can use Flibl to transfer that text and keep some important information that would otherwise be lost. 

The basic steps to convert from ELAN to FLEx are:

1. Create a ELAN to FLEx configuration file per the instructions in the next heading.
2. Place your configuration file, ELAN file, and the scripts from this repository in the same directory.
3. Open the command line and navigate to the directory from 2.
4. Run Flibl.
    * Run the following
    ```shell
    python flextext_construction.py
    ```
    * If you are using a Mac, you will probably need to run it using
    ```shell
    python3 flextext_construction.py
    ```
    * The script will generate a new FLExText file in the same directory where your original EAF file was. The FLExText will have a long name that has the date and time of running Flibl, to avoid confusion and version clashing if things go wrong or you need to redo/fix something. You can edit the name after generating the file.
5. Import the FLExText to your FLEx database.
    * Within FLEx, open the Texts and Words pane
    * Click File at the top left > Import > FLExText Interlinear 
    * Navigate to your newly created file and choose it

## Settings Configuration
In order to get started with the ELAN to FLEx conversion, you need to create a configuration file. At this stage, you will need to do this by modifying `to_flextext_config.json` (from this repository) directly in a text editor. Future versions of Flibl will allow users to create the JSON interactively in a browser instead.

When you're setting up the config file for processing multiple files, you can include the information for all the texts and Flibl will only use what is relevant for a given file when it is processing it. That said, make sure that none of the information is contradictory (e.g. if a Tier Type is not to be included in one text but is in another).

The next section explains what all of the fields in the configuration file mean.

## Fields in `to_flextext_config`
### File names
- **What is this for?** Put your file names here. If you put your ELAN file and the Python files in the same folder, you can use just the name of your EAF. If you put them in different folders, you'll need to enter the "absolute" path. This might begin with your drive name, such as `C://...`, or with a leading slash `/`. For example, something like `/home/mycomputer/Documents/language-work/recordings/rec1_20240103.eaf` would be an absolute path.
- **Example**:
    - EAF in same folder as Python scripts (relative path):
         ```json
         "file_names": ["rec1_20240103.eaf"]
         ```
    - EAF in different folder from Python scripts (absolute path):
         ```json
         "file_names": ["C://Documents/language_project/recordings/rec1_20240103.eaf"]
         ```

### Language fonts
- **What is this for?** This section provides information for FLEx about language, script, and font. 
    - **Language/`lang`:** the code used by FLEx to identify this language/script. Give the FLEx code (e.g. "es" for Spanish). Often this is only two letters for the Analysis language but three letters (frequently corresponding to the ISO 639-3 code) for the Vernacular language. You will have specified this code when you set up your project. It's also used as part of the project sync settings if you use LanguageDepot.
    - **font:** the name of the font used in FLEx for this language
    - **vernacular:** "true" or "false" - true if the language is going to be treated as a language of "study", false if it is only used for the translations and/or notes. For example, a person studying Quechua but translating and glossing in Spanish would put "true" on the line describing Quechua, and "false" on the line about Spanish.
- **Example**:
    - Spanish as analysis language, Quechua (qup) as study language:
        ```json
      "language_fonts":
        [{"lang": "es", "font":"Charis SIL", "vernacular":"false"},
        {"lang":"qup", "font":"Charis SIL", "vernacular":"true"}]
        ```
- **Additional information**
    - You will almost certainly have at least two languages, with one being vernacular and the other the analysis language (i.e. not the vernacular language).
    - If you are using Flibl to analyze child language, you need to decide if you want FLEx to treat the children's utterances as being the same language as the adults'. The benefit of treating them as different languages is that the children's ungrammatical forms won't go into the adult lexicon or train the morphological parser used on adult utterances.
      To treat the children and adults' utterances as different, you'll need to define a separate vernacular language in the FLEx project for each one. For example, the Ayöök project treats the adults' utterances as the language `mto` but the children's as `cps` (this is an ISO code chosen for convenience - it is the official code for an unrelated language spoken in a different part of the world).
      You will also need to assign the child and adult languages different fonts.
    - For all of this information, go into FLEx and find it under Tools > Configure > Set up Vernacular/Analysis Writing Systems. You'll find the code under the General tab, and the font under the Font tab.
        - How to access the Set Up Writing Systems dialogs:
          
         ![Screenshot from FLEx, in the Texts & Words panel, following the above described path to an option box that includes Set up Vernacular Writing Systems... and Set up Analysis Writing Systems...](/readme_screenshots/font_setup.png)
      
        - After choosing Set Up Writing Systems, how to find the code for a language:
          
         ![Screenshot from FLEx, within the box that comes up after choosing one of the Set up Writing Systems options, showing a General tab active, with a Code below it and the text "mto" next to that](/readme_screenshots/writing_sys_code.png)
        
        - After choosing Set Up Writing Systems, how to find the font for a language:
          
         ![Screenshot from FLEx, within the box that comes up after choosing one of the Set up Writing Systems options, showing a Font tab active, with "Default font" below it and the text "Noto Sans" within a drop-down box](/readme_screenshots/writing_sys_font.png)

### Languages
- **What is this for?**: here you should put in the names of the writing systems for the languages you are working with. These should correspond with the codes you gave above in the "Language fonts" section.
    - **Primary vernacular writing sys**: the equivalent of FLEx's "vernacular" language, but more specifically is the code you are using for the language of study in FLEx.
    - **Child language writing sys**: if you are setting up child/ungrammatical utterances as a different writing system, this is where you should put that code.
    - **FLEx language writing sys**: the language you have configured FLEx to use, such as English (en), Spanish (es), or Portuguese (pt), among others.
- **Example**:
   - Treating adult and child Ayöök (mto) as different languages:
        ```json
        "languages": {"main_language": "mto", "child_language": "cps", "flex_language": "en"}
        ```

### Valid characters
- **What is this for?**: Flibl needs to know which characters are used to make words, as the script requires a search among all of utterances to separate words (a.k.a. tokenization). In order to make this work, please provide an exhaustive list of all characters that FLEx will consider word-forming. Flibl takes this input as a [Regular Expression](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions/Cheatsheet). To get you started, here is the set of all majuscule and miniscule (upper and lower case) characters in the Latin alphabet: `A-Za-z`. Add to that string any other characters you use, if you're using the Latin alphabet and, e.g., accent marks (so for Spanish it would be `A-Za-zÁáÉéÍíÓóÚúü`). Make sure not to add a space because then it will consider spaces to be parts of words, and therefore not break up strings that have words separated by spaces.
- **Example** for the Ayöök orthography:
  ```json
  "valid_characters": {"main_language": "A-Za-zäëöüÄËÖÜ'`ꞌꞋ'‘’\u00E4\u00EB\u00F6\u00FC\u00C4\u00CB\u00D6\u00DC\u0308áéíóúÁÉÍÓÚ\u00E1\u00E9\u00ED\u00F3\u00FA\u00C1\u00C9\u00CD\u00D3\u00DA",
  "child_language": "A-Za-zäëöüÄËÖÜ'`ꞌꞋ'’\u00E4\u00EB\u00F6\u00FC\u00C4\u00CB\u00D6\u00DC\u0308áéíóúÁÉÍÓÚ\u00E1\u00E9\u00ED\u00F3\u00FA\u00C1\u00C9\u00CD\u00D3\u00DA"}
  ```
        
- **Additional information**
    - You only need to do this with "vernacular" languages (i.e. not any lingua francas/"analysis languages"). FLEx needs to separate the words of a text before importing it, but this is not important for the Free Translations
    - You'll need to make sure FLEx will consider all of these characters as word-forming and not punctuation, which can be adjusted in the Writing systems configuration in FLEx. Refer back to the screenshots above to get to the Vernacular Writing System Properties window and click on the Characters tab, then click on Valid Characters... . Use this interface to see which characters FLEx sees as valid for the "vernacular" language, (adjust it if you haven't before,) and use the Word Forming set at the top to make your Regular Expression for the configuration file.
      
      The Valid Characters dialog looks like this:
      ![Screenshot from FLEx showing the writing system character setup. On the right are two sets of characters, one in a box labelled "Word forming" and the other, below, labelled "Punctuation, Symbols & Spaces". Both boxes have characters that would correspond to those sets.](/readme_screenshots/valid_char_choices.png)

    - Since many writing systems use glottal stops marked by some kind of apostrophe-like symbol, but there's a ton that look similar but are indeed different, here's a bunch of apostrophes so you can allow all of them, just in case the wrong kind snuck into your text: '`ꞌꞋ'‘’. If you want to check the Unicode escape for a character, we recommend [this UniView app](https://r12a.github.io/uniview/index.html), where you can copy and paste a character into the box and see information about it, or go the other direction and start from information about a character like its Unicode block name or escape and see the character itself. Another option is thie [Unicode code converter](https://r12a.github.io/app-conversion/index.html) which also lets you go in both directions, and you can just type an entire string in whichever box is appropriate for what you're trying to do.

### Exclude tier IDs
- **What is this for?**: Give IDs of specific tiers you would like to exclude from the transfer here. Find the ID of your tiers in the same way as you found their types: At the top of the ELAN window, click "Tiers" then "Change Tier Attributes...", then look for the Tier Name field for the tiers you would like to exclude.
- **Example**:
  ```json
  "exclude_tier_ids": ["ayöök", "observaciones", "comentarios", "inglés", "Interlinear-title-mto"]
  ```
- **Additional information**
    - Make sure you're putting the Tier Name here for all tiers to exclude, rather than types
    - If you have tiers that are not dependent on any time-aligned transcription tiers, please put them here (or if they all use the same Type, include that Type in the "Exclude tier types" field below).

### Exclude tier types
- **What is this for?**: Give types of specific tiers you would like to exclude from the transfer here. Find the ID of your tiers in the same way as you found their types: At the top of the ELAN window, click "Tiers" then "Change Tier Attributes...", then look for the Tier Type field for the tiers you would like to exclude.
- **Example**:
     ```json
     "exclude_tier_types": ["Words"]
     ```
- **Additional information**
    - Make sure you're putting the Tier Type here for all Tier Types to exclude, rather than specific names
    - Make sure that you don't input a Tier Type that is used for any tiers you want to include!
    - If you want to exclude an entire Type, you do not need to add the Tiers that are of that type explicitly in the previous field.

### Exclude tier constraints
- **What is this for?**: If there are entire stereotypes of tiers you would like to exclude from the transfer, include them here. These are found by looking at the top of the ELAN window for "Type" > "Change Tier Type", and looking for the Stereotype of each of the Tier Types. One might want to do this if they have Symbolic Subdivision or Included In tiers where the annotations are not important to keep for transfer to FLEx, and it would be more efficient to exclude the entire Stereotype instead of individually naming all of the types that use it.
- **Example**:
     ```json
     "exclude_tier_constraints": ["Symbolic Subdivision", "Included In"] 
     ```
- **Additional information**
    - Make sure that you don't input a Stereotype that is used for any tiers you want to include!
    - If you want to exclude an entire Stereotype, you do not need to add the Types nor Tiers that it applies to explicitly in the previous fields
    - The reason this field refers to "tier constraints" instead of "stereotypes" is because technically, in ELAN, the stereotypes themselves are not what constrain the usage; rather there is a description of how the stereotypes are constrained in each ELAN file and it always starts off with the same rules. Hence, it is the constraints themselves that are important. We want the names of the stereotypes that they apply to, though, because that is the best way to actually find them in the file.

### Translation tiers
- **What is this for?**: Include the names and language codes of the tiers used for translations in the ELAN file.
    - **Translation tier name**: The Tier Name of a translation tier (see information on "Exclude tier IDs" for finding the name of a Tier)
    - **Translation lang code**: the language code in FLEx that the translation belongs to. This should be one of the languages you give above in "Language fonts".
- **Example**:
  ```json
  "translation_tiers":{
  "FIL_Translation-gls-es":"es",
  "YDN_Translation-gls-es":"es",
  "YDNM_Translation-gls-es":"es",
   "YDNB_Translation-gls-es":"es",
  "FILS_Translation-gls-es":"es"
  }
  ```
- **Additional information**
    - The translation tiers should be associated with (i.e. dependent on) a parent tier. This parent tier is most often a transcription tier. Flibl will be able to identify and find this parent, but don't give the names of any orphan tiers.

### Target utterance tier type
- **What is this for?**: This is a list of Tier Types that are being used to store the target/grammatical equivalents of child/ungrammatical utterances.
- **Example**:
  ```json
      "target_utterance_tier_type": ["Target Utterance"]
  ```
- **Additional information**
    - Note that all target tiers must have the same Tier Type and that this field is for the Tier *Type*, not the tier name. See above for more information on finding this in the ELAN interface. 

# Going from FLEx to ELAN
Once you have a text that has been parsed to your satisfaction in FLEx, you can now export it and use Flibl to ensure that it keeps important information as you open it in ELAN. If you have gone through the process of exporting from FLEx and importing to ELAN before, this will be different - Flibl foregoes the built-in Import process in ELAN and creates the EAF file for you instead.

1. Export the text from FLEx
    * From File, click Export Interlinear...
    * Choose to export as a FLExText (this should be the first option; the Format column will say "ELAN, SayMore, FLEx" and the Extention column will say "FLEXTEXT")
    * Choose all the files you wish to export
    * Select a place for them to be saved and export them
2. Set up the configuration file following the detailed instructions below.
3. Place the FLExText, original EAF, configuration file, and scripts from this repository in the same directory.
4. Open the command line and navigate to the directory from 3.
5. Run Flibl
    * Run the following
    ```shell
    python eaf_construction.py
    ```
    * If you are using a Mac, you will probably need to run it using
    ```shell
    python3 eaf_construction.py
    ```
    * The terminal window will fill up with numbers. This is just noting the percentage of utterances that have been parsed by Flibl, so you can see the progress.
    * If you want to also export a JSON representation of the file, you can add a flag to do so. It will create a JSON file with the same name that you can use and manipulate in other programs and scripts, more easily than a FLExText or EAF XML format:
    ```shell
    python eaf_construction.py -j
    ```
    or, on a Mac
    ```shell
    python3 eaf_construction.py -j
    ```
6. Open it in ELAN just like you would open any other EAF file.

Hooray! You now have created an EAF file that has the results of parsing in FLEx, re-associating ungrammatical and grammatical utterances, and with all the note tiers appropriately settled where you wanted them. Just sort by date to see which one was most recently made in the source folder where you kept your FLExText, and you'll see it. It will have an even longer title, with the date and time you used Flibl to create this file (so it will have the date and time of both import and export if you used Flibl in both directions) for the same reason as above--i.e., in case something goes wrong or you need to edit something and redo the export. You'll be able to open that file directly in ELAN without a formal import--it maintains the link to media it originally had, too, so you don't need to set that up. You can edit the name of the output file if needed.

If you want to process your data in R, you can now scrape the ELAN file to a nested tibble object in R using the `eaf_to_table_control.R` script included in this repository. Download both R scripts (`eaf_to_table_control.R` and `eaf_to_table_functions.R`), place them in the same directory. Open `eaf_to_table_control.R`, add your file names, and follow the commented instructions in the script to scrape your data.

## Settings configuration
In order to get started on the FLEx to ELAN export process, you need to create a configuration file. For the time being, you should do this by modifying the JSON file, `to_eaf_config.json`, directly in a text editor. (Future/beta versions of Flibl will allow you to create the config file interactively in a browser.) 

When you're setting up the config file for processing multiple files, you can include the information for all the texts. Flibl will only use what is relevant for a given file when it is processing it. That said, make sure that none of the information is contradictory (e.g. if a speaker is not to be considered a "kid" in one text but is in another).

## Fields in `to_eaf_config.json`

### File names
- **What is this for?**: should contain the names of each file that will be processed when running this. We advise using one file at first just to make sure everything is working as it should. Remember to check that the path is correct. A notable difference between this and the ELAN -> FLEx script is that you need to have the paths to both the original ELAN file *as well as* the new FLExText you just exported. This is so that metadata from the original ELAN file is maintained in the import.
    - **Original EAF**: A filepath for the original EAF file that was made into a FLExText for glossing
    - **FLExText**: A filepath for the glossed FLExText that was just exported from FLEx
- Example
    ```json
    "eafs_flextexts":[
        {
            "original_eaf":"/home/Documents/work/recordings/text0.eaf",
            "flextext":"/home/Documents/work/recordings/text0-glossed.flextext"
        }
    ]
    ```
- **Additional information**
    - See the information about file names in the section about going from ELAN to FLEx--the instructions about absolute vs relative path apply here as well.

### Language
- **What is this for?**: the "Vernacular" language code, according to FLEx.
- Example:
     ```json
     "language": "mto"
     ```
- **Additional information**
    - This is the *language code* in FLEx. See the instructions above for the ELAN to FLExText export for information about finding this information in FLEx.

### Child language
- **What is this for?**: If you set up child/ungrammatical utterances as a different language from adult/grammatical utterances in FLEx, enter the child language code here.
- Example:
     ```json
     "child_language": "cps"
     ```
- **Additional information**
    - If you didn't have Child/Ungrammatical utterances using a different language code, you do not need this.

### Speakers
- **What is this for?**: This is information about the speakers who are represented in the ELAN file. FLEx keeps information about the speakers in some ways, but gets rid of a lot of it in the re-export (which is partially why we need to have the original EAF to refer to when constructing the new one).
    - **Name**: The code used for the speaker (i.e. what appears in the Note line in FLEx, based on the original speakers in ELAN). Find this information by looking at the Tier Attributes for your Tiers and looking at the Participant field.
    - **Kid**: `1` if the speaker has both actual/ungrammatical and target/grammatical utterances coded on separate tiers in the EAf. `0` if the speaker would not have these tiers. Setting to `1` makes Flibl look for matchups of corresponding Phonetic-Target utterance pairs
- Example: This is for an EAF with adult speakers named FIL, FILS, and YDNM, and child speakers named YDN and YDNB.
    ```json
    "speakers":{
        "FIL":{
            "name":"FIL",
            "kid":0
        },
        "FILS":{
            "name":"FILS",
            "kid":0
        },
        "YDNM":{
            "name":"YDNM",
            "kid":0
        },
        "YDNB":{
            "name":"YDNB",
            "kid":1
        },
        "YDN":{
            "name":"YDN",
            "kid":1
        }
    },
    ```
- **Additional information**
    - For speaker attributions to work, you must fill in the Participant attribute for every tier in your original EAF. Check that your Participant attributes are complete in the Tiers > Change Tier Attributes dialog in ELAN. 
    - We use the term "speaker" because this workflow is oriented toward spoken language transcription, translation, and glossing. FLEx is incompatible with workflows for signed modalities and ELAN is incompatible with workflows for written modalities, hence the specific use of "speaker".

### Translations
- **What is this for?**: a list of the language codes for the languages used for translation in FLEx
- Example:
     ```json
     "translations": ["es", "en"]
     ```

### Languages
- **What is this for?**: a list of all languages used, with fields for information needed by ELAN. To prevent confusion, it's helpful to keep them all three fields the same. But if you have a system, please use it! It's mostly important for controlled vocabularies, which are assumed to be in an `unk` (unknown) language, and ELAN will default to filling it out as such.
    - `LANG_DEF`: reference for the language (often a URI, somehow might link to an outside page with information; rarely used)
    - `LANG_ID`: internal identifier for the language (how ELAN refers to the language within the program)
    - `LANG_LABEL`: external label for the language (what we see in the interface of ELAN)
- Example:
    ```json
    "languages":[
        {
            "LANG_DEF":"mto",
            "LANG_ID":"mto",
            "LANG_LABEL":"mto"
        },
        {
            "LANG_DEF":"es",
            "LANG_ID":"es",
            "LANG_LABEL":"es"
        },
        {
            "LANG_DEF":"cps",
            "LANG_ID":"cps",
            "LANG_LABEL":"cps"
        }
    ]
    ```
    
### XDS
- **What is this for?**: a list of controlled vocabulary items for addressee coding. Called "XDS" for "X-directed speech", a cover term for "adult-directed speech," "child-directed speech," etc. Flibl will look for notes in the FLExText that consist of items from this controlled vocabulary, then it will construct a tier for them in the output EAF.
- Example: From the controlled vocabulary used in the sample input EAF
    ```json
    "xds":[
        "A",
        "A+C",
        "C",
        "T",
        "T+A",
        "T+C",
        "T+C+A",
        "ANTA",
        "ANTC",
        "ANTS",
        "U"
    ]
    ```
- **Additional information**
    - If you don't have a tier with XDS, you don't need to worry about it. If you want to use this tier for some other purpose, nothing will break. An example of an alternative use case would be if you have a controlled vocabulary of codes for a particular construction is used (e.g. [CASE MATCH], [CASE MISMATCH]). If you want a tier that has only these codes, you can enter them in this field. Again, Flibl will look for these controlled vocabulary items in the *Notes*, not strings within the transcribed text.

# FAQ
## What the heck is "command line"? What happens if I mess something up?
Using the command line can look a bit scary! It seems like you're a hacker all of a sudden and that might make you think that you have just a bit more power than you're comfortable with. First of all, definitely make sure you have backups. Secondly, know that nothing in this program will ever overwrite or delete existing files. Rather, it will create files and these will be labelled based on date and time that they were created so you can know which run of Flibl was used for the creation of it.
## Is there seriously no way to do this with a graphical user interface (GUI)?
This is a slightly more complicated and ideological question. The short answer is yes, there is a way to do this with a GUI, but at the loss of maximal compatibility and flexibility. 
