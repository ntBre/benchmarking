#[derive(Debug, PartialEq)]
pub struct Histogram {
    pub(crate) min: f64,
    pub(crate) max: f64,
    pub(crate) counts: Vec<usize>,
}

impl Histogram {
    pub fn new(data: &[f64], bins: usize) -> Self {
        if data.is_empty() {
            panic!("can't construct an empty histogram");
        }
        let min = *data.iter().min_by(|a, b| a.total_cmp(b)).unwrap();
        let max = *data.iter().max_by(|a, b| a.total_cmp(b)).unwrap();
        let mut counts = vec![0; bins];
        for d in data {
            let idx = bins as f64 * (d - min) / (max - min);
            counts[(idx as usize).clamp(0, bins - 1)] += 1;
        }
        Self { min, max, counts }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn basic() {
        let got = Histogram::new(&[0.5, 1.5, 2.5, 3.5, 4.9], 5);
        let want = Histogram {
            min: 0.5,
            max: 4.9,
            counts: vec![1, 1, 1, 1, 1],
        };
        assert_eq!(got, want);
    }
}
