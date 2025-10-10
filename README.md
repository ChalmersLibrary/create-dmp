Script for creating new DMP:s (projects) in DS Wizard from a tab separated file with metadata and new Project records in Chalmers CRIS (research.chalmers.se), possibly enriched with data from a secondary source, such as SweCRIS or GDP.

Assumes a (minimum) input file in the following format (esp. note name orientation and e-mail address used (should ideally correspond with the e-mail returned by the Idp, but the script will try and look this up from Chalmers PDB):        
2021-05377	Einstein Albert   albert.einstein@chalmers.se   Formas        

The script will try and create the user (and set permissions) if not already found in DSW. It will also (if selected) send e-mails to the researchers after DMP and CRIS project have been created, using a set of pre-defined, funder specific templates.    

Copy env_example to .env and add current values to get started. Settings (paths) in create-new-dmp.conf need to be adjusted to the selected DSW KM.    

Please use the staging environment (dsw-staging.xxx) and (at least initially) set send_emails to "false" when testing!     

Can be used in conjunction with our other DS Wizard services, such as:   
https://github.com/ChalmersLibrary/dsw2es        
https://github.com/ChalmersLibrary/cth-dmps-api   

