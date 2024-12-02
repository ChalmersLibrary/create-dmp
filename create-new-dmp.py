#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
from dotenv import load_dotenv
import csv
from datetime import datetime
import os
import random
import string
import uuid
import configparser
import logging

# Script for creating new DMP:s (projects) in DS Wizard from a tab separated file with metadata
# and new Project records in Chalmers CRIS,
# possibly enriched with data from a secondary source, such as SweCRIS or GDP.
#
# Assumes a (minimum) input file in the following format (esp. note name orientation and e-mail address used
# (should correspond with the e-mail returned by the Idp)!):
# 2021-05377	Olsson Louise   louise.olsson@chalmers.se	0000-0002-8308-0784
#
# / urban.andersson@chalmers.se

# Settings
load_dotenv()
dswurl = os.getenv("DSW_URL")
dswuser = os.getenv("DSW_USER")
dswpw = os.getenv("DSW_PW")
infile = os.getenv("INFILE")
logfile = os.getenv("LOGFILE")
packageid = os.getenv("PACKAGE_ID")
templateid = os.getenv("TEMPLATE_ID")
create_cris_projects = os.getenv("CREATE_CRIS_PROJECTS")

# Read config
config = configparser.ConfigParser()
config.read_file(open(r'create-new-dmp.conf'))

dsw_token = ''
try:
    dsw_authurl = dswurl + '/tokens'
    auth_data = dict(email=dswuser, password=dswpw)
    data_auth = requests.post(url=dsw_authurl, json=auth_data, headers={'Accept': 'application/json'}).text
    data_auth = json.loads(data_auth)
    dsw_token = data_auth['token']
except requests.exceptions.HTTPError as e:
    print('Could not authenticate with DSW, user: ' + dswuser + ' , existing.')
    with open(os.getenv("LOGFILE"), 'a') as lf:
        lf.write('Could not authenticate with DSW, user: ' + dswuser + ' , exiting: ' + e.response.text)
    sys.exit(1)

headers = {'Accept': 'application/json',
           'Authorization': 'Bearer ' + dsw_token}

# Open and read input file
with open(infile) as infile_txt:
    csv_reader = csv.reader(infile_txt, delimiter='\t')
    for row in csv_reader:
        print(f'{row[1]}')
        useruuid = ''
        pw = ''

        # Initial variables, change according to input file
        # Assumes inverted names, change below otherwise
        projectid = row[1]
        name = row[2]
        email = row[3]
        orcid = row[5]
        cth_personid = row[4]
        lname = name.split()[0].strip()
        fname = name.split()[1].strip()
        dname = fname + ' ' + lname
        auth_data = []
        newuser_data = []
        dmp_data = []
        cris_project = dict()
        project_cris_id = 0
        cris_project_url = ''

        # Initialize other parameters with test data
        project_title = 'Default test project'
        project_title_swe = ''
        project_desc = 'This is the description. More to follow... ÅÄÖåäö'
        project_desc_swe = ''
        project_start = '2022-01-01'
        project_end = '2025-12-31'
        funder_name = os.getenv("FUNDER_NAME")
        funderid = os.getenv("FUNDER_ID")
        funder_suffix = os.getenv("FUNDER_SUFFIX")

        # Fetch data from SweCRIS, if not available in the Prisma spreadsheet
        swecris_url = os.getenv("SWECRIS_URL") + projectid + '_' + funder_suffix
        swecris_headers = {'Accept': 'application/json',
                           'Authorization': 'Bearer ' + os.getenv("SWECRIS_API_KEY")}
        try:
            swecrisdata = requests.get(url=swecris_url, headers=swecris_headers).text
            if 'Internal server error' in swecrisdata:
                print('No data for id: ' + projectid + ' was found in SweCRIS! Skipping to next.')
                continue
            swecrisdata = json.loads(swecrisdata)
            print('Got data from SweCRIS!')
            project_title = swecrisdata['projectTitleEn']
            project_title_swe = swecrisdata['projectTitleSv']
            project_desc = swecrisdata['projectAbstractEn']
            project_desc_swe = swecrisdata['projectAbstractSv']
            # Check what field to use for each funder!
            #project_start = swecrisdata['fundingStartDate']
            #project_end = swecrisdata['fundingEndDate']
            project_start = swecrisdata['projectStartDate']
            project_end = swecrisdata['projectEndDate']
            # Note: Project start/end date needs to be 'yyyy-mm-dd' in DSW, comes as 'yyyy-mm-dd hh:ss:sss' from Swecris
        except requests.exceptions.HTTPError as e:
            print('No data for id: ' + projectid + ' was found in SweCRIS! Skipping to next.')
            print('\n')
            with open(os.getenv("LOGFILE"), 'a') as lf:
                lf.write('No data for id: ' + projectid + ' was found in SweCRIS! Skipping to next.')
            continue

        # Lookup user in DSW and get Uuid, or create new if user don't exist
        dsw_getuser = dswurl + '/users?q=' + str(email)
        userdata = requests.get(url=dsw_getuser, headers=headers).text
        userdata = json.loads(userdata)
        if userdata['_embedded']['users']:
            useruuid = userdata['_embedded']['users'][0]['uuid']
            print('user exists! id: ' + str(useruuid))
        else:
            print('user DOES NOT exist, creating NEW user!')
            # Create new user
            try:
                newuser_url = dswurl + '/users'
                pw = ''.join(random.choice(string.ascii_letters) for i in range(44))
                newuser_data = dict(email=email, lastName=lname, firstName=fname, role='researcher', password=pw,
                                    affiliation='Chalmers')
                data_newuser = requests.post(url=newuser_url, json=newuser_data, headers=headers).text
                data_newuser = json.loads(data_newuser)
                useruuid = data_newuser['uuid']
                print('User ' + email + ' created with id: ' + useruuid + ' and pw: ' + pw)
                # Activate new user
                user_activate_url = dswurl + '/users/' + useruuid
                try:
                    activate_data = dict(email=email, active=True, lastName=lname, firstName=fname, role='researcher',
                                         affiliation='Chalmers')
                    data_activate = requests.put(url=user_activate_url, headers=headers).text
                    print('User: ' + useruuid + ' has been activated.')
                except requests.exceptions.HTTPError as e:
                    print('Could not activate user with e-mail: ' + email + '.')
                    with open(os.getenv("LOGFILE"), 'a') as lf:
                        lf.write('Could not activate user: ' + email + '.' + e.response.text)
                    sys.exit(1)
            except requests.exceptions.HTTPError as e:
                print('Could not create user with e-mail: ' + email + '.')
                sys.exit(1)

        # Create new dmp
        print('Creating new DMP with title: ' + project_title + '.')
        try:
            create_dmp_url = dswurl + '/questionnaires'
            create_data = dict(questionTagUuids=[config.get('Paths', 'question.tag.uuids')], packageId=packageid,
                               templateId=templateid, visibility='PrivateQuestionnaire',
                               sharing='RestrictedQuestionnaire', name=project_title,
                               formatUuid='d3e98eb6-344d-481f-8e37-6a67b6cd1ad2', state='Default', isTemplate=False)
            data_create = requests.post(url=create_dmp_url, json=create_data, headers=headers).text
            data_create = json.loads(data_create)
            dmpuuid = data_create['uuid']
            print('Dmp ' + project_title + ' created with id: ' + dmpuuid)
        except requests.exceptions.HTTPError as e:
            print('Could not create DMP with name: ' + project_title + '.')
            with open(os.getenv("LOGFILE"), 'a') as lf:
                lf.write('Could not create DMP: ' + project_title + '.' + e.response.text + '\n')
            sys.exit(1)

        # Add content to dmp

        # Mandatory field in API, set to default values for all (it will be fine)
        phases_answered_dict = dict(answeredQuestions=7, indicationType='PhasesAnsweredIndication',
                                    unansweredQuestions=1)

        start_path = dict(path=config.get('Paths', 'start'),
                          phasesAnsweredIndication=phases_answered_dict,
                          value=dict(value=[config.get('Paths', 'contributor.uuid')], type='ItemListReply'),
                          uuid=str(uuid.uuid4()),
                          type='SetReplyEvent')

        name_dict = dict(
            path=config.get('Paths', 'name.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=dname, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        email_dict = dict(
            path=config.get('Paths', 'email.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=email, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        orcid_dict = dict(
            path=config.get('Paths', 'orcid.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=orcid, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        aff_dict = dict(
            path=config.get('Paths', 'aff.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=config.get('Paths', 'aff.choice.cth'), type='AnswerReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        role_dict = dict(
            path=config.get('Paths', 'role.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=config.get('Paths', 'role.choice.contact'), type='AnswerReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_dict = dict(
            path=config.get('Paths', 'project.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=['7e2925a6-3e9f-4226-bcaa-4c18ea216933'], type='ItemListReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_name_dict = dict(
            path=config.get('Paths', 'project.name.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=project_title, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_desc_dict = dict(
            path=config.get('Paths', 'project.desc.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=project_desc, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_start_dict = dict(
            path=config.get('Paths', 'project.start.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=project_start[0:10], type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_end_dict = dict(
            path=config.get('Paths', 'project.end.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=project_end[0:10], type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        funding_dict = dict(
            path=config.get('Paths', 'funding.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=['7e2925a6-3e9f-4226-bcaa-4c18ea216933'], type='ItemListReply'),
            type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        funder_dict = dict(
            path=config.get('Paths', 'funder.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=dict(value=funder_name, id=funderid, type='IntegrationType'), type='IntegrationReply'),
            type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        project_status_dict = dict(
            path=config.get('Paths', 'status.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=config.get('Paths', 'status.choice.granted'), type='AnswerReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        grantid_dict = dict(
            path=config.get('Paths', 'grant.id.path'),
            phasesAnsweredIndication=phases_answered_dict,
            value=dict(value=projectid, type='StringReply'), type='SetReplyEvent',
            uuid=str(uuid.uuid4()))
        phase_dict = dict(
            phaseUuid=config.get('Paths', 'phase.uuid'),
            phasesAnsweredIndication=phases_answered_dict,
            type='SetPhaseEvent',
            uuid=str(uuid.uuid4())
        )    

        dmp_data = dict(events=[start_path, name_dict, email_dict, orcid_dict, aff_dict, role_dict, project_dict,
                                project_name_dict, project_desc_dict, project_start_dict, project_end_dict,
                                funding_dict, funder_dict, project_status_dict, grantid_dict, phase_dict])
        # print(dmp_data)

        try:
            newdmp_url = dswurl + '/questionnaires/' + dmpuuid + '/content'
            print(dmp_data)
            data_newdmp = requests.put(url=newdmp_url, json=dmp_data, headers=headers).text
            # data_newdmp = json.loads(data_newdmp)
            # print('status: ' + str(data_newdmp.status_code))
            print('DMP ' + dmpuuid + ' updated with content.')
        except requests.exceptions.HTTPError as e:
            print('Could not update DMP with id: ' + dmpuuid + '.')
            sys.exit(1)

        # Alter ownership of dmp
        dmp_owner_data = dict(
            sharing='RestrictedQuestionnaire', visibility='PrivateQuestionnaire',
            permissions=[dict(memberType='UserQuestionnairePermType',
                memberUuid=useruuid, perms=['VIEW', 'COMMENT', 'EDIT', 'ADMIN'])]
        )

        try:
            dmpowner_url = dswurl + '/questionnaires/' + dmpuuid + '/share'
            data_dmpowner = requests.put(url=dmpowner_url, json=dmp_owner_data, headers=headers).text
            print('DMP ' + dmpuuid + ' changed owner to ' + useruuid)
        except requests.exceptions.HTTPError as e:
            print('Could not alter DMP with id: ' + dmpuuid + '.')
            sys.exit(1)

        # Create Project in Chalmers CRIS (if selected)

        if create_cris_projects == 'true':
            dmp_url = os.getenv("DSW_UI_URL") + '/projects/' + dmpuuid
            # Check if Project already exists
            cris_check_url = os.getenv("CRIS_API_URL") + '/ProjectSearch?query="' + projectid + '"+AND+"' + os.getenv("CRIS_FUNDERID") + '"'
            checkdata = requests.get(url=cris_check_url, headers={'Accept': 'application/json'}).text
            checkdata = json.loads(checkdata)
            if checkdata['TotalCount'] == 1:
                print("Project " + projectid + " already exists in CRIS. Add DMP manually!")
                project_cris_id = 0
            else:
                print("A new CRIS project record will be created for project " + projectid)
                # Create CRIS Project object
                current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                contract_org = dict(Id=os.getenv("CRIS_FUNDERID"))
                contract_id = dict(ProjectContractIdentifierID=2, ProjectContractIdentifierValue=projectid)
                contract = dict(ContractSource='dsw', ContractStartDate=project_start[0:10] + 'T00:00:00',
                                ContractEndDate=project_end[0:10] + 'T00:00:00', DmpValue=dmp_url, DmpVersion=1,
                                ContractOrganization=contract_org, OrganizationID=os.getenv("CRIS_FUNDERID"),
                                ContractIdentifiers=[contract_id], CreatedDate=current_date, CreatedBy='dsw')
                # Get Person from CRIS
                # If we already have Research Person IDs, the first step could be skipped
                person_cris_id = cth_personid
                persons = []
                person = dict()
                # try:
                #     person_get_url = os.getenv(
                #         "CRIS_PERSON_URL") + '/Persons?idValue=' + email + '&idTypeValue=EMAIL&maxCount=1&selectedFields=Id'
                #     person_crisdata = requests.get(url=person_get_url, headers={'Accept': 'application/json'}).text
                #     person_crisdata = json.loads(person_crisdata)
                #     if person_crisdata['TotalCount'] == 0:
                #         print(
                #             "Person with e-mail " + email + " not found in CRIS. Skip and add project " + projectid + " manually!")
                #         print('\n')
                #         project_cris_id = 0
                #         # Print output to logfile and continue with next
                #         current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                #         with open(os.getenv("LOGFILE"), 'a') as lf:
                #             lf.write(
                #                 current_date + '\t' + projectid + '\t' + project_title + '\t' + fname + ' ' + lname + '\t' + email + '\t' + os.getenv(
                #                     "DSW_UI_URL") + '/projects/' + dmpuuid + '\t' + str(
                #                     project_cris_id) + '\t' + cris_project_url + '\n')
                #         print('\n')
                #         continue
                #     else:
                #         person_cris_id = person_crisdata['Persons'][0]['Id']
                # except requests.exceptions.HTTPError as e:
                #     print('Person lookup failed. Skip and add project ' + projectid + ' manually!')
                #     print('\n')
                #     project_cris_id = 0
                #     # Print output to logfile and continue with next
                #     current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                #     with open(os.getenv("LOGFILE"), 'a') as lf:
                #         lf.write(
                #             current_date + '\t' + projectid + '\t' + project_title + '\t' + fname + ' ' + lname + '\t' + email + '\t' + os.getenv(
                #                 "DSW_UI_URL") + '/projects/' + dmpuuid + '\t' + str(
                #                 project_cris_id) + '\t' + cris_project_url + '\n')
                #     print('\n')
                #     continue

                # Get Person OrgHome from CRIS
                person_org_cris_id = ''
                # person_orghome_name = ''
                person_org = dict()
                try:
                    person_org_get_url = os.getenv(
                        "CRIS_PERSON_URL") + '/Persons/' + person_cris_id + '/OrganizationHomes?year=' + os.getenv(
                        "CRIS_YEAR") + '&currentOnly=true&maxLevelDepartment=true'
                    person_org_crisdata = requests.get(url=person_org_get_url,
                                                       headers={'Accept': 'application/json'}).text
                    person_org_crisdata = json.loads(person_org_crisdata)
                    person_org_cris_id = person_org_crisdata['OrganizationId']
                    # person_orghome_name = person_org_crisdata['OrganizationData']['OrganizationParents'][0]['ParentOrganizationData']['DisplayNameSwe']
                    person_org = dict(OrganizationID=person_org_cris_id)
                except requests.exceptions.HTTPError as e:
                    print('Person org lookup failed. Skip and add project ' + projectid + ' manually!')
                    print('\n')
                    project_cris_id = 0
                    # Print output to logfile and continue with next
                    current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                    with open(os.getenv("LOGFILE"), 'a') as lf:
                        lf.write(
                            current_date + '\t' + projectid + '\t' + project_title + '\t' + fname + ' ' + lname + '\t' + email + '\t' + os.getenv(
                                "DSW_UI_URL") + '/projects/' + dmpuuid + '\t' + str(
                                project_cris_id) + '\t' + cris_project_url + '\n')
                    print('\n')
                    continue

                person = dict(PersonID=person_cris_id, PersonOrganizations=[person_org], PersonRoleID=1)

                project_start_cris = project_start[0:10] + 'T00:00:00'
                project_end_cris = project_end[0:10] + 'T00:00:00'

                cris_project = dict(
                    ProjectTitleEng=project_title, ProjectTitleSwe=project_title_swe,
                    ProjectDescriptionEng=project_desc,
                    ProjectDescriptionEngHtml='<p>' + project_desc + '</p>', PublishStatus=1,
                    ProjectDescriptionSwe=project_desc_swe,
                    ProjectDescriptionSweHtml='<p>' + project_desc_swe + '</p>',
                    StartDate=project_start_cris,
                    EndDate=project_end_cris, ProjectSource='SweCRIS', CreatedDate=current_date,
                    CreatedBy='dsw',
                    Contracts=[contract], Persons=[person]
                )

                # Debug
                # print(cris_project)

                # Add Project to CRIS
                create_project_url = os.getenv("CRIS_API_URL") + '/Projects'
                try:
                    project_create = requests.post(url=create_project_url, json=cris_project, headers=headers).text
                    project_create = json.loads(project_create)
                    print(project_create)
                    project_cris_id = project_create['ID']
                    print('Project ' + projectid + ' created with id: ' + str(project_cris_id))
                    cris_project_url = os.getenv("CRIS_URL") + '/en/project/' + str(project_cris_id)
                except requests.exceptions.HTTPError as e:
                    print('Could not create Project with name: ' + project_title + ' in CRIS. Add manually!')
                    # Print output to logfile and continue with next
                    current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                    with open(os.getenv("LOGFILE"), 'a') as lf:
                        lf.write(
                            current_date + '\t' + projectid + '\t' + project_title + '\t' + fname + ' ' + lname + '\t' + email + '\t' + os.getenv(
                                "DSW_UI_URL") + '/projects/' + dmpuuid + '\t' + str(
                                project_cris_id) + '\t' + cris_project_url + '\n')
                    print('\n')
                    continue

        # Ready
        # Print output to logfile and continue with next
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        with open(os.getenv("LOGFILE"), 'a') as lf:
            lf.write(
                current_date + '\t' + projectid + '\t' + project_title + '\t' + fname + ' ' + lname + '\t' + email + '\t' + os.getenv(
                    "DSW_UI_URL") + '/projects/' + dmpuuid + '\t' + str(
                    project_cris_id) + '\t' + cris_project_url + '\n')
        print('\n')
