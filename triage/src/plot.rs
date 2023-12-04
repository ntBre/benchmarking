#![allow(unused)]

use std::path::Path;

use image::{Rgb, RgbImage};

use crate::{histogram::Histogram, plot::convert::Converter, point};

use self::point::Point;

mod color {
    use image::Rgb;

    #[inline]
    pub(crate) const fn rgb(hex: u32) -> Rgb<u8> {
        let red = hex >> 0x10;
        let green = (hex >> 0x8) & 0xff;
        let blue = hex & 0xff;
        Rgb([red as u8, green as u8, blue as u8])
    }

    pub(crate) type Rgb8 = Rgb<u8>;

    pub(crate) const RED: Rgb8 = rgb(0xff0000);
    pub(crate) const GREEN: Rgb8 = rgb(0x00ff00);
    pub(crate) const BLUE: Rgb8 = rgb(0x0000ff);
}

mod point {
    #[derive(Debug)]
    pub(crate) struct Point<T> {
        pub(crate) x: T,
        pub(crate) y: T,
    }

    impl<T> Point<T> {
        pub(crate) fn new(x: T, y: T) -> Self {
            Self { x, y }
        }
    }

    #[macro_export]
    macro_rules! point {
        ($x:expr, $y:expr) => {
            $crate::plot::point::Point::new($x, $y)
        };
    }
}

mod convert {
    //! Convert between data and canvas dimensions

    use super::point::Point;

    /// fields prefixed with a `d` refer to numerical data, while those prefixed
    /// with a `c` refer to canvas coordinates
    #[derive(Debug)]
    pub(crate) struct Converter {
        pub(crate) dminx: f64,
        pub(crate) dmaxx: f64,
        pub(crate) dminy: f64,
        pub(crate) dmaxy: f64,
        pub(crate) cminx: u32,
        pub(crate) cmaxx: u32,
        pub(crate) cminy: u32,
        pub(crate) cmaxy: u32,
    }

    impl Converter {
        /// returns the width and height of the canvas
        const fn canvas_dimensions(&self) -> (u32, u32) {
            (self.cmaxx - self.cminx, self.cmaxy - self.cminy)
        }

        /// returns the width and height of the data
        fn data_dimensions(&self) -> (f64, f64) {
            (self.dmaxx - self.dminx, self.dmaxy - self.dminy)
        }

        /// convert `p` to canvas units
        pub(crate) fn to_canvas(&self, p: Point<f64>) -> Point<u32> {
            let (cw, ch) = self.canvas_dimensions();
            let (dw, dh) = self.data_dimensions();
            let fx = p.x / dw; // fraction of data x
            let fy = p.y / dh; // fraction of data y

            // fractional x and y values
            let x = fx * cw as f64;
            let y = fy * ch as f64;

            // translate based on minimum canvas position and invert y
            let x = x + self.cminx as f64;
            let y = self.cmaxy as f64 - y;

            // considered clamping to canvas dimensions here, but it seems
            // better just to overflow and not draw rather than saturate to the
            // edges
            Point {
                x: x as u32,
                y: y as u32,
            }
        }
    }
}

struct Cursor {
    col: Rgb<u8>,
}

pub struct Plot {
    img: RgbImage,
    cur: Cursor,
}

impl Plot {
    pub fn new(width: u32, height: u32) -> Self {
        Self {
            img: RgbImage::from_pixel(width, height, color::rgb(0xe2e2e2)),
            cur: Cursor {
                col: color::rgb(0xff0000),
            },
        }
    }

    pub fn to_file(&self, path: impl AsRef<Path>) {
        self.img.save(path).unwrap();
    }

    pub fn set_color(&mut self, rgb: Rgb<u8>) {
        self.cur.col = rgb;
    }

    pub fn histogram(&mut self, data: &[f64]) {
        let hist = Histogram::new(data, 15);
        let (mw, mh) = self.img.dimensions();
        // let the actual plot occupy 80% of the width and height
        let w = mw * 1 / 10;
        let h = mh * 1 / 10;
        self.rect(point!(w, h), point!(mw - w, mh - h));

        let buf = 10;
        let conv = Converter {
            dminx: hist.min,
            dmaxx: hist.max,
            dminy: 0.0,
            dmaxy: *hist.counts.iter().max().unwrap() as f64,
            cminx: w + buf,
            cmaxx: mw - w - buf,
            cminy: h + buf,
            cmaxy: mh - h,
        };

        let bin_width = (hist.max - hist.min) / hist.counts.len() as f64;
        for (i, bin) in hist.counts.iter().enumerate() {
            let start = i as f64 * bin_width;
            let end = (i + 1) as f64 * bin_width;
            let p1 = conv.to_canvas(point!(start, *bin as f64));
            let p2 = conv.to_canvas(point!(end, 0.0));
            self.rect(p1, p2);
        }
    }

    // primitives

    /// draws an empty rectangle from the upper left corner (`p1`) to the lower
    /// right corner (`p2`), inclusive of the endpoints using the current color
    fn rect(&mut self, p1: Point<u32>, p2: Point<u32>) {
        let Point { x: x1, y: y1 } = p1;
        let Point { x: x2, y: y2 } = p2;

        // horizontal lines
        for x in x1..=x2 {
            self.img.put_pixel(x, y1, self.cur.col);
            self.img.put_pixel(x, y2, self.cur.col);
        }

        for y in y1..=y2 {
            self.img.put_pixel(x1, y, self.cur.col);
            self.img.put_pixel(x2, y, self.cur.col);
        }
    }

    /// draws a filled rectangle from the upper left corner (`p1`) to the lower
    /// right corner (`p2`), inclusive of the endpoints using the current color
    fn fill(&mut self, p1: Point<u32>, p2: Point<u32>) {
        let Point { x: x1, y: y1 } = p1;
        let Point { x: x2, y: y2 } = p2;

        // horizontal lines
        for x in x1..=x2 {
            for y in y1..=y2 {
                self.img.put_pixel(x, y, self.cur.col);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{plot::color::rgb, point};

    #[test]
    fn test_rgb() {
        assert_eq!(rgb(0xff0000), Rgb([255, 0, 0]));
        assert_eq!(rgb(0x00ff00), Rgb([0, 255, 0]));
        assert_eq!(rgb(0x0000ff), Rgb([0, 0, 255]));
        assert_eq!(rgb(0xffffff), Rgb([255, 255, 255]));
        assert_eq!(rgb(0xf0f1f2), Rgb([240, 241, 242]));
    }

    #[test]
    fn basic() {
        let mut p = Plot::new(320, 320);
        p.rect(point!(10, 10), point!(310, 310));
        p.set_color(color::BLUE);
        p.fill(point!(40, 40), point!(280, 280));
        p.set_color(color::GREEN);
        p.fill(point!(80, 80), point!(240, 240));
        p.to_file("/tmp/basic.png");
    }

    #[test]
    fn hist() {
        let mut p = Plot::new(480, 320);
        p.histogram(&[
            9.24046, 5.93909, 3.06394, 5.78941, 7.40133, 7.86926, 4.3637,
            3.32195, 7.7888, 1.00887, 7.85084, 8.35159, 7.61209, 4.96077,
            4.26298, 9.45798, 8.21802, 7.09269, 1.57828, 1.19752, 9.09685,
            8.68084, 4.49256, 7.05432, 3.99686, 6.45049, 6.96163, 3.00211,
            5.91664, 9.56569, 1.56318, 7.96877, 1.32388, 5.48236, 9.84306,
            8.23073, 4.22985, 9.64365, 7.93915, 1.73531, 5.68816, 9.3252,
            2.05224, 0.199054, 8.4918, 7.26009, 7.58101, 1.97576, 7.48589,
            4.33507, 4.66232,
        ]);
        p.to_file("/tmp/hist.png");
    }
}
