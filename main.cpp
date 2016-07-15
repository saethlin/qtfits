#include <CCfits>
#include <cmath>
#include <QApplication>
#include <QImage>
#include <QPixmap>
#include <QTextStream>
#include "label.h"

using namespace CCfits;

int main(int argc, char *argv[]) {

    std::auto_ptr<FITS> pInfile(new FITS("test.fits",Read,true));
    PHDU& image = pInfile->pHDU(); 
    std::valarray<unsigned long>  contents;
    image.read(contents);

    QApplication app(argc, argv);

    QImage qim = QImage(100, 100, QImage::Format_Mono);
    qim.fill(0);
    QPixmap pixmap;
    pixmap.convertFromImage(qim);

    Label window;
    window.setWindowTitle("QLabel");
    window.show();

    return app.exec();
}
