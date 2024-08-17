cmake_minimum_required(VERSION 3.28)
project(easyLinux)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS -I../include)
# 查找 wxWidgets 库
find_package(wxWidgets REQUIRED COMPONENTS core base)

# 包含 wxWidgets 编译器和链接器标志
include(${wxWidgets_USE_FILE})

# 添加源文件
add_executable(easyLinux src/main.cpp
        include/easyLinux/EasyLinux.h
        src/easyLinux/EasyLinux.cpp
        include/easyLinux/MainFrame.h
        src/easyLinux/MainFrame.cpp)

# 链接 wxWidgets 库
target_link_libraries(easyLinux ${wxWidgets_LIBRARIES})
