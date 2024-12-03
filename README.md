Script for creating new DMP:s (projects) in DS Wizard from a tab separated file with metadata and new Project records in Chalmers CRIS (research.chalmers.se), possibly enriched with data from a secondary source, such as SweCRIS or GDP.

Assumes a (minimum) input file in the following format (esp. note name orientation and e-mail address used (should correspond with the e-mail returned by the Idp):   
2021-05377	Einstein Albert   albert.einstein@chalmers.se	0000-0002-2222-3333   
The script will try and create the user if not already found in DSW.

Copy env_example to .env and add current values to get started. Settings (paths) in create-new-dmp.conf need to be adjusted to the selected DSW KM.
