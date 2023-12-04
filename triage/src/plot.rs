#![allow(unused)]

use std::path::Path;

use image::{Rgb, RgbImage};

#[inline]
const fn rgb(hex: u32) -> Rgb<u8> {
    let red = hex >> 0x10;
    let green = (hex >> 0x8) & 0xff;
    let blue = hex & 0xff;
    Rgb([red as u8, green as u8, blue as u8])
}

type Rgb8 = Rgb<u8>;

const RED: Rgb8 = rgb(0xff0000);
const GREEN: Rgb8 = rgb(0x00ff00);
const BLUE: Rgb8 = rgb(0x0000ff);

struct Cursor {
    col: Rgb<u8>,
}

pub struct Plot {
    img: RgbImage,
    cur: Cursor,
}

struct Point {
    x: u32,
    y: u32,
}

impl Point {
    fn new(x: u32, y: u32) -> Self {
        Self { x, y }
    }
}

macro_rules! point {
    ($x:expr, $y:expr) => {
        Point::new($x, $y)
    };
}

impl Plot {
    pub fn new(width: u32, height: u32) -> Self {
        Self {
            img: RgbImage::from_pixel(width, height, rgb(0xe2e2e2)),
            cur: Cursor { col: rgb(0xff0000) },
        }
    }

    pub fn to_file(&self, path: impl AsRef<Path>) {
        self.img.save(path).unwrap();
    }

    pub fn set_color(&mut self, rgb: Rgb<u8>) {
        self.cur.col = rgb;
    }

    // primitives

    /// draws an empty rectangle from the upper left corner (`p1`) to the lower
    /// right corner (`p2`), inclusive of the endpoints using the current color
    fn rect(&mut self, p1: Point, p2: Point) {
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
    fn fill(&mut self, p1: Point, p2: Point) {
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
        p.set_color(BLUE);
        p.fill(point!(40, 40), point!(280, 280));
        p.set_color(GREEN);
        p.fill(point!(80, 80), point!(240, 240));
        p.to_file("/tmp/triage.png");
    }
}
