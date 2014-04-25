 cmake_minimum_required(VERSION 2.8)
#-----------------------------------------------------------------------------
set(MODULE_NAME FastGrowCutEffect)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  ${MODULE_NAME}.png
  )

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})


#-----------------------------------------------------------------------------
ctkMacroCompilePythonScript(
  TARGET_NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_ROOT}
  )
  
add_subdirectory(FastGrowCut)
include(${Slicer_EXTENSION_CPACK})

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()


