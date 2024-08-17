//
// Created by cat on 2024/8/17.
//

#include "easyLinux/EasyLinux.h"
#include "easyLinux/MainFrame.h"

bool EasyLinux::OnInit() {
    auto *frame = new MainFrame("Hello, wxWidgets!");
    frame->Show(true);
    return true;
}