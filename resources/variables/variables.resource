*** Variables ***
${ENV}   v1
${SUTv1}    localhost:5085
${SUTv2}    localhost:5095

##########################

#A1
${FILE_MANAGER_LOCATOR}    //*[@id="sidebar"]/div/div[1]/div/ul/li[7]/a/span

#A4
${SCRIPT_DROPDOWN}     name:script
#S1
${STATISTICS_TEXT_LOCATOR}    //*[@id="main-content"]/main/div/div[1]/div[2]/h3
#S2
${DATATABLES_LINK}    //*[@id="dropdown-dashboard"]/li[1]/a

${CHARTS_LINK}        //*[@id="dropdown-dashboard"]/li[2]/a
${API_LINK}           //*[@id="dropdown-dashboard"]/li[3]/a
${TASKS_LINK}         //*[@id="dropdown-dashboard"]/li[4]/a

${USER_PROFILE_MENU}    //*[@id="user-menu-button-2"]/img
${SIGN_IN_DROPDOWN}     //*[@id="dropdown-2"]/ul/li[2]/a
${STATISTICS_TABLE_LOCATOR}    //*[@id="main-content"]/main/div/div[1]/div[2]


##
##