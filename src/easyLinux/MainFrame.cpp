//
// Created by cat on 2024/8/17.
//

#include "easyLinux/MainFrame.h"

MainFrame::MainFrame(const wxString& title)
       : wxFrame(nullptr, wxID_ANY, title) {
    auto *panel = new wxPanel(this, wxID_ANY);
    auto *text = new wxStaticText(panel, wxID_ANY,
                        "Hello, wxWidgets!",
                        wxPoint(10, 10));

    // 实际使用 text 变量，消除 CLion 警告
    text->SetLabel("Updated Label");
    std::cout << "OK" << std::endl;
}