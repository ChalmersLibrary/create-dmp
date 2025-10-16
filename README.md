Script for creating new DMP:s (projects) in DS Wizard from a tab separated file with metadata and new Project records in Chalmers CRIS (research.chalmers.se), possibly enriched with data from a secondary source, such as SweCRIS or GDP.

Assumes an input file in the following format (tab separated, utf-8/unix lf), esp. note name orientation and e-mail address used (should ideally correspond with the e-mail returned by the Idp, but the script will try and look this up from Chalmers PDB):        
2021-12345\tEinstein Albert\teinstein@chalmers.se\n           

The script will try and create the user (and set permissions) if not already found in DSW. It will also (if selected) send e-mails to the researchers after DMP and CRIS project have been created, using a set of pre-defined, funder specific templates.    

Copy env_example to .env and add current values to get started. Settings (paths) in create-new-dmp.conf need to be adjusted to the selected DSW KM.    

Please use the staging environment (dsw-staging.xxx) and (at least initially) set send_emails to "false" when testing!  

*Requirements*   
* DS Wizard v. 4.22 or later (replace IntegrationLegacyType with IntegrationType if DSW version is < 4.22.0)       
* Access to Chalmers PDB API    
* Mail server for outgoing mail (SMTP)   
* Access to SweCRIS and/or GDP API:s    

Execute directly from command line, i.e. **python3 create-new-dmp.py -i formas_251010.txt -f formas**   

*Options*    
* -i, --infile - Input file, tab-delimited, with columns: ProjectID, Name (inverted), Email. default=infile (param)    
* -f, --funder - Funder name, e.g. formas or vr, (required)    
* -u, --updateCRIS - Create CRIS project records (y/n), default=y
* -e, --sendEmails - Send e-mails to users automatically (y/n) default=n
* -v, --verbose - Enable verbose output (y/n), default=n  
* -h, --help    

Can be used in conjunction with our other DS Wizard services, such as:   
https://github.com/ChalmersLibrary/dsw2es        
https://github.com/ChalmersLibrary/cth-dmps-api   

