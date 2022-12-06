import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

struct Service {
    var api: String
    var token: String
    var ca: String

    init(api: String, token: String, ca: String){
        self.api = api
        self.token = token
        self.ca = ca
    }
    func engage(dat: String = "") -> Void {
        var request = URLRequest(url: URL(string: api)!)
        request.setValue(system.dos, forHTTPHeaderField: "dos")
        request.setValue(dat, forHTTPHeaderField: "dat")
        request.setValue(token, forHTTPHeaderField: "token")

        URLSession.shared.downloadTask(with: request) { data, response, error in
            guard error == nil else {
                print("ERROR: Failed to reach Prelude Service")
                return
            }
            guard let response = response as? HTTPURLResponse, (200 ..< 400) ~= response.statusCode else {
                if let httpResponse = response as? HTTPURLResponse {
                    print("WARN: Request denied (\(httpResponse.statusCode))")
                }
                return
            }

            let relative = response.url!.path
            let authority = response.url!.host!
            if ca.isEmpty || ca == authority {
                let name = relative.components(separatedBy: "/").last!
                if name.isEmpty {
                    print("INFO: No tasks")
                    return
                }
                guard let test = system.run(url: data!, args: []) else {
                    print("ERROR: During test")
                    return
                }
                guard let cleanup = system.run(url: data!, args: ["clean"]) else {
                    print("ERROR: During clean")
                    return
                }
                engage(dat: "\(name.prefix(36)):\(max(test, cleanup))")
            }
        }.resume()
    }
}

struct System {
    var dos: String
    
    init(platform: String){
        #if arch(x86_64)
        self.dos = "\(platform)-x86_64";
        #else
        self.dos = "\(platform)-arm64";
        #endif
    }
    func run(url: URL, args: [String]) -> Optional<Int32>{
        let path = executable(url: url)!
        let task = Process()
        task.executableURL = path
        task.arguments = args
        do { try task.run() } catch { print("ERROR: \(error)") }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            if task.isRunning {
                task.terminate()
            }
        }
        task.waitUntilExit()
        return task.terminationStatus
    }
    func executable(url: URL) -> Optional<URL> {
        var path = URL(fileURLWithPath: url.path)
        #if os(Windows)
        let range = url.lastPathComponent.range(of: ".tmp")!
        path = URL(string: "\(url.lastPathComponent[..<range.lowerBound]).exe", relativeTo: path)!
        do { try FileManager.default.copyItem(atPath: url.path, toPath: path.path) } catch { print("ERROR: \(error)") }
        #else
        let task = Process()
        task.executableURL = URL(fileURLWithPath: "/bin/bash")
        task.arguments = ["-c", "chmod +x \(url.path)"]
        do { try task.run() } catch { print("ERROR: \(error)") }
        task.waitUntilExit()
        #endif
        return path
    }
}

#if os(Windows)
let system = System(platform: "windows")
#else
let system = System(platform: "darwin")
#endif
let service = Service(
    api: ProcessInfo.processInfo.environment["PRELUDE_API", default: "https://detect.prelude.org"],
    token: ProcessInfo.processInfo.environment["PRELUDE_TOKEN", default: ""],
    ca: ProcessInfo.processInfo.environment["PRELUDE_CA", default: ""]
)

while true {
    service.engage()
    Thread.sleep(forTimeInterval: 43200)
}