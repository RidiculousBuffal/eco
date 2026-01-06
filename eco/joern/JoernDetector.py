import subprocess
import tempfile
import os
from pathlib import Path


class JoernAdvisor:
    def __init__(self):
        self.script_path = Path(os.path.join(os.path.dirname(os.path.relpath(__file__)),'detectors.sc')).absolute().as_posix()
        self.docker_image = "ghcr.io/joernio/joern:master"

    def analyze_code(self, code: str) -> list[str]:

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path_local = Path(tmp_dir).absolute().as_posix()
            code_file_local = Path(tmp_dir) / "input.cpp"
            code_file_local.write_text(code,encoding='utf-8')
            mount_code = f"{tmp_path_local}:/src"
            mount_script = f"{self.script_path}:/scripts/detectors.sc"

            try:
                subprocess.run([
                    "docker", "run", "--rm",
                    "-v", mount_code,
                    self.docker_image,
                    "joern-parse", "/src/input.cpp", "--output", "/src/app.cpg"
                ], check=True, capture_output=True, text=True)

                result = subprocess.run([
                    "docker", "run", "--rm",
                    "-v", mount_code,
                    "-v", mount_script,
                    self.docker_image,
                    "joern",
                    "--script", "/scripts/detectors.sc",
                    "--param", "cpgPath=/src/app.cpg"
                ], capture_output=True, text=True, check=True,encoding='utf-8')

                return self._parse_output(result.stdout)

            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else e.stdout
                print(f"Error during Joern analysis:\n{error_msg}")
                return [f"Analysis failed: {error_msg}"]

    def _parse_output(self, raw_stdout: str) -> list[str]:
        diagnoses = []
        for line in raw_stdout.splitlines():
            line = line.strip()
            if "🔍" in line:
                diagnoses.append(line)
        return diagnoses


if __name__ == "__main__":
    advisor = JoernAdvisor()

    test_code = """
    #include <iostream>
    #include <vector>
    #include <algorithm>
    using namespace std;

    int fib(int n) {
        if (n <= 1) return n;
        return fib(n-1) + fib(n-2);
    }

    int main() {
        int n;
        cin >> n;
        vector<int> v = {1, 2, 3};
        sort(v.begin(), v.end());
        cout << fib(n) << endl;
        return 0;
    }
    """

    print("正在启动 Joern 容器进行分析...")
    results = advisor.analyze_code(test_code)
    for r in results:
        print(r)
    """
    🔍 Method fib at lines 7 uses pure recursion.
    🔍 Vector 'v' at line 15 is static.
    🔍 Slow I/O detected at line 14: cin >> n
    🔍 Slow I/O detected at line 17: cout << fib(n) << endl
    """
