Are you converting EAFs that contain child/learner speech *and* annotations of the target/adult-like form for (at least some) child utterances? 

If so, use the example files in the `has_child_language` directory. 

Otherwise, use the example files in the `no_child_language` directory.

Example files are in Ticuna. They were created in Cushillococha, Loreto, Peru by the following participants:

* `no_child_language`: Lesli Victoria Guerrero Coello (speaker), Menrys Farias Gomez (speaker), Liceth Farias Guerrero (speaker), various bystanders (speakers), anonymous transcriber, Amalia Skilton (researcher).
  * Recorded and transcribed in 2022.
  * Recordings are archived as [California Language Archive 2018-19.155](http://dx.doi.org/doi:10.7297/X2TH8KT0).
  * Several children speak on the recording, but their speech is *not* annotated with target forms and therefore this is a 'no child language' recording.
* `has_child_language`: Child aged 1 year, 2 months at recording date (speaker); her mother/primary caregiver (speaker); child and adult bystanders (speakers); Angel Bittancourt Serra (transcriber); Amalia Skilton (researcher). Recording participants are anonymous due to ethics requirements.
  * Recorded in 2019 and transcribed in 2022.
  * Recordings are archived as [California Language Archive 2018-19.060](http://dx.doi.org/doi:10.7297/X2T72FPH)

In both files, the time-aligned transcription tiers have the type `tca` and use an ASCII-only practical orthography. The `no_child_language` file also has transcription tiers in the official Peruvian Ticuna orthography with the type `tca-po`. Only the `tca` tiers are imported to FLEx with these config files.
