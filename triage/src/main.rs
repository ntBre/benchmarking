use std::{collections::HashMap, fs::read_to_string};

fn avg(v: &[f64]) -> f64 {
    v.iter().sum::<f64>() / v.len() as f64
}

fn std(v: &[f64]) -> f64 {
    let u = avg(v);
    (v.iter().map(|vi| (vi - u).powi(2)).sum::<f64>() / v.len() as f64).sqrt()
}

fn extract_key(k: &(String, Vec<f64>)) -> u8 {
    match (&k.0[1..]).find(|c: char| c.is_ascii_alphabetic()) {
        Some(n) => &k.0[1..=n],
        None => &k.0[1..],
    }
    .parse()
    .unwrap()
}

fn main() {
    // this is ~3x faster than from_reader, despite the large size of the file
    let h: HashMap<String, Vec<f64>> =
        serde_json::from_str(&read_to_string("../../triage.json").unwrap())
            .unwrap();

    let mut bonds = Vec::new();
    let mut angles = Vec::new();
    let mut torsions = Vec::new();
    let mut impropers = Vec::new();
    for pair in h {
        match pair.0.chars().next().unwrap() {
            'a' => angles.push(pair),
            'b' => bonds.push(pair),
            't' => torsions.push(pair),
            'i' => impropers.push(pair),
            _ => unimplemented!(),
        }
    }

    bonds.sort_by_key(extract_key);
    angles.sort_by_key(extract_key);
    torsions.sort_by_key(extract_key);
    impropers.sort_by_key(extract_key);

    for (vec, label) in [
        (bonds, "Bonds"),
        (angles, "Angles"),
        (torsions, "Torsions"),
        (impropers, "Impropers"),
    ] {
        println!("{}", label);
        for (k, v) in vec {
            println!("{k:>5} {:8} {:12.8} {:12.8}", v.len(), avg(&v), std(&v));
        }
    }
}
