*** Settings ***
Library    SeleniumLibrary
Library    libraries/SelfHealLibrary.py
Library    libraries/SelfHealGit.py
Resource    resources/keywords/keywords.resource
Resource    resources/variables/variables.resource
Variables    libraries/llm_prompts.py

Test Setup         Open SUT
Test Teardown      Teardown With Self Healing
#Test Teardown     Close Browser

*** Variables ***
${GPT3}            openai/gpt-3.5-turbo
${GPT4}            openai/gpt-4-turbo
${GPT4o}           openai/gpt-4o
${MISTRAL}         mistralai/mistral-7b-instruct
${MIXTRAL}         mistralai/mixtral-8x22b-instruct
${MISTRAL_L}       mistralai/mistral-large
${LLAMA}           meta-llama/llama-3-8b-instruct
${LLAMA70}         meta-llama/llama-3-70b-instruct
${CLAUDE}          anthropic/claude-3-sonnet

${LLM}             ${GPT4}
${SELF_HEALING}    ON
${CANDIDATE_LEVEL}  STRONG   #STRONG  #or WEAK

*** Keywords ***
Open SUT
    Open Browser     ${SUT${ENV}}
    Go To   ${SUT${ENV}}

Teardown With Self Healing
    IF  '${SELF_HEALING}' == 'ON'
        IF  '${TEST STATUS}' == 'FAIL'
            Make Request For Llm    ${LLM}
        END
    END
    Close Browser

#############################
#############################


*** Test Cases ***
File Manager Visible At Sidebar
    [Documentation]    A1
#    ...                SUT Change: Naming "PRO File Manager" to "File Manager"
    [Tags]     A1
    Wait Until Page Contains Element    ${FILE_MANAGER_LOCATOR} 
    Element Text Should Be    ${FILE_MANAGER_LOCATOR}    PRO File Manager

Theme Can Be Toggled To Dark Mode
    [Documentation]    A2
#    ...                SUT Change: id:theme-toggle to id:theme-toggler
    [Tags]    A2

    Wait Until Page Contains Element    id:theme-toggle
    Click Element    id:theme-toggle

Navigation To Starter Page From Sidebar Is Functional
    [Documentation]    A3
#    ...                SUT change: starter href:/starter/ to href:/start/
    [Tags]    A3
    Wait Until Page Contains Element   link:Starter Page  
#    Click Link    xpath=//*[@href="/starter/"]
#    Click is is not usable, problem with selenium library
#    Unexpected when saving locator to DB: Element with locator 'xpath=//*[@href='/starter/']' not found., <class 'SeleniumLibrary.errors.ElementNotFound'>

Tasks List Scripts Can Be Changed
    [Documentation]    A4
#    ...    SUT change: name:script locator to name:scripts
    [Tags]    A4 
    Navigate To Tasks Page
    Change Script To Clean Database

Navigation To Sign In Page Is Functional
    [Documentation]    A5
#    ...                SUT change: button type from type:submit to type:button
    [Tags]    A5
    Navigate To Sign In Page
    Page Should Contain Element    //*[@type="submit"]

Dashboard Search Has Label Attached
    [Documentation]    A6
#    ...                SUT change: class from class:sr-only to class:search-only
    [Tags]    A6
    Wait Until Page Contains Element     class:sr-only
    Element Text Should Be    class:sr-only    Search 

Statistics Table Visible At Dashboard
    [Documentation]    S1
#    ...                SUT change: Removing DIV from page which will affect the xpath
    [Tags]     S1
    Wait Until Page Contains Element    ${STATISTICS_TABLE_LOCATOR}
    Element Should Contain     ${STATISTICS_TEXT_LOCATOR}    Statistics this month

All Apps Are Visible At Sidebar
    [Documentation]    S2
#    ...                SUT change: Switching position of API Link. API will be first in the list.
#    ...                S2 - Based on index - API link has switched position which will break test
    [Tags]     S2
    DataTables Link Is Visible
    Charts Link Is Visible
    API Link Is Visible
    Tasks Link Is Visible

##
##
##
##