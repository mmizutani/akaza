#[cfg(test)]
mod tests {
    use libakaza::akaza_builder::{Akaza, AkazaBuilder};

    fn load_akaza() -> anyhow::Result<Akaza> {
        let datadir = env!("CARGO_MANIFEST_DIR").to_string() + "/../../akaza-data/data/";
        AkazaBuilder::default()
            .system_data_dir(datadir.as_str())
            .build()
    }

    fn test(yomi: &str, kanji: &str) -> anyhow::Result<()> {
        let got = load_akaza()?.convert_to_string(yomi)?;
        assert_eq!(got, kanji);
        Ok(())
    }

    #[test]
    fn test_wnn() -> anyhow::Result<()> {
        test("わたしのなまえはなかのです", "私の名前は中野です")
    }

    #[test]
    fn test_working() -> anyhow::Result<()> {
        test(
            "ろうどうしゃさいがいほしょうほけんほう",
            "労働者災害補償保険法",
        )
    }
}