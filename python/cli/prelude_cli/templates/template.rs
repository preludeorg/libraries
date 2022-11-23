/*
NAME: $NAME
QUESTION: $QUESTION
CREATED: $CREATED
*/
fn test() {
    println!("Run test");
    std::process::exit(100);
}

fn clean() {
    println!("Clean up");
    std::process::exit(100);
}

fn main() {
    if std::env::args().len() > 1  {
        clean()
    } else {
        test();
    }
}