using System;

class TTP {
    static int Test() {
        Console.WriteLine("Testing");
        return 0;
    }

    static int Clean() {
        Console.WriteLine("Clean");
        return 0;
    }

    static void Main(string[] args) {
        if (args[0].Contains("clean")) {
            Clean();
        } else {
            Test();
        }
    }
}
