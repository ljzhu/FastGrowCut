 cmake_minimum_required(VERSION 2.8)


#-----------------------------------------------------------------------------
set(MODULE_NAME FastGrowCutEffect)


set(EXTENSION_HOMEPAGE " https://www.slicer.org/slicerWiki/index.php/Documentation/4.3/Modules/FastGrowCut")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_STATUS "Beta")
set(EXTENSION_CONTRIBUTORS "Liangjia Zhu, Ivan Kolesov,  Allen Tannenbaum (Stony Brook University), Yi Gao, (UAB), and Ron Kikinis (BWH) ")
set(EXTENSION_DESCRIPTION "This is a fast implementation of the GrowCut method that supports multi-label segmetnations")
set(EXTENSION_ICONURL "https://www.slicer.org/slicerWiki/index.php/File:FastGrowCutEffect.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/slicerWiki/index.php/File:FastGrowCutScreenShot.png")

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


