cmake_minimum_required(VERSION 3.5)

# TODO: Project version
project(robodk_api_cxx VERSION 1.0.0)

# Set the install location
set(CMAKE_INSTALL_PREFIX "../install")

# Find dependencies
find_package(Qt5 NAMES Qt5 COMPONENTS Widgets GUI Concurrent Core Network REQUIRED)

# TODO: Option for static vs shared
add_library(robodk_api_cxx STATIC robodk_api.cpp)

# Set the public header for the library so it can be installed
set_target_properties(robodk_api_cxx PROPERTIES PUBLIC_HEADER robodk_api.h)
# Set the include directories
target_include_directories(robodk_api_cxx PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  )

# Link the target to its dependent libraries
target_link_libraries(robodk_api_cxx PUBLIC Qt5::Gui Qt5::Core Qt5::Network)

# Specify where to install targets and define the EXPORT target name
install(TARGETS robodk_api_cxx 
  EXPORT robodk_api_cxxTargets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
  PUBLIC_HEADER DESTINATION include
  )

# Install the exported target
install(EXPORT robodk_api_cxxTargets
  FILE "robodk_api_cxxTargets.cmake"
  NAMESPACE "robodk_api_cxx::"
  DESTINATION cmake
  )

# Create the Config and Version files
include(CMakePackageConfigHelpers)
configure_package_config_file(${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/robodk_api_cxxConfig.cmake"
  INSTALL_DESTINATION cmake
  )

write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/robodk_api_cxxConfigVersion.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY AnyNewerVersion
  )

# Install the Config and Version Files
install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/robodk_api_cxxConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/robodk_api_cxxConfigVersion.cmake
  DESTINATION cmake
  )
