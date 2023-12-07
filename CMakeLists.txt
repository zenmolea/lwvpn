cmake_minimum_required(VERSION 3.0)
project(dsvpn)

set(MY_PYBIND pybind11)

add_subdirectory(${MY_PYBIND})

set(SOURCES
    src/vpn.cpp
    src/charm.cpp
    src/os.cpp
)

set(HEADERS
    include/charm.h
    include/vpn.h
    include/os.h
)

include_directories(include)

pybind11_add_module(lwvpn ${SOURCES} ${HEADERS})

#add_executable(dsvpn ${SOURCES} ${HEADERS})




