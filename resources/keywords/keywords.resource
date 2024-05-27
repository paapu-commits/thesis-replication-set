*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
DataTables Link Is Visible
    Page Should Contain Element    ${DATATABLES_LINK}
    Element Text Should Be    ${DATATABLES_LINK}    DataTables

Charts Link Is Visible
    Page Should Contain Element     ${CHARTS_LINK}
    Element Text Should Be    ${CHARTS_LINK}    Charts

API Link Is Visible
    Page Should Contain Element     ${API_LINK}
    Element Text Should Be    ${API_LINK}    API
    
Tasks Link Is Visible
    Page Should Contain Element    ${TASKS_LINK}
    Element Text Should Be    ${TASKS_LINK}    Tasks

Navigate To Sign In Page
    Wait Until Page Contains Element    ${USER_PROFILE_MENU}
    Click Element    ${USER_PROFILE_MENU}
    Wait Until Page Contains Element    ${SIGN_IN_DROPDOWN}
    Click Element    ${SIGN_IN_DROPDOWN}

Navigate To Tasks Page
    Wait Until Page Contains Element    ${TASKS_LINK}
    Click Element    ${TASKS_LINK}
    Wait Until Page Contains    Async Tasks Manager

Change Script To Clean Database
    Page Should Contain Element    ${SCRIPT_DROPDOWN}
    Click Element    ${SCRIPT_DROPDOWN}