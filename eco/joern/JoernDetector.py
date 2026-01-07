import asyncio
import tempfile
import os
from pathlib import Path


class JoernAdvisor:
    def __init__(self):
        # 这里的路径处理逻辑保持不变
        self.script_path = Path(
            os.path.join(os.path.dirname(os.path.relpath(__file__)), 'detectors.sc')).absolute().as_posix()
        self.docker_image = "ghcr.io/joernio/joern:master"

    async def analyze_code(self, code: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path_local = Path(tmp_dir).absolute().as_posix()
            code_file_local = Path(tmp_dir) / "input.cpp"

            code_file_local.write_text(code, encoding='utf-8')

            mount_code = f"{tmp_path_local}:/src"
            mount_script = f"{self.script_path}:/scripts/detectors.sc"

            try:
                parse_process = await asyncio.create_subprocess_exec(
                    "docker", "run", "--rm",
                    "-v", mount_code,
                    self.docker_image,
                    "joern-parse", "/src/input.cpp", "--output", "/src/app.cpg",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                _, stderr = await parse_process.communicate()

                if parse_process.returncode != 0:
                    raise Exception(f"Joern parse failed: {stderr.decode('utf-8')}")

                analyze_process = await asyncio.create_subprocess_exec(
                    "docker", "run", "--rm",
                    "-v", mount_code,
                    "-v", mount_script,
                    self.docker_image,
                    "joern",
                    "--script", "/scripts/detectors.sc",
                    "--param", "cpgPath=/src/app.cpg",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await analyze_process.communicate()

                if analyze_process.returncode != 0:
                    error_msg = stderr.decode('utf-8')
                    print(f"Error during Joern analysis:\n{error_msg}")
                    return [f"Analysis failed: {error_msg}"]

                return self._parse_output(stdout.decode('utf-8'))

            except Exception as e:
                return [f"Analysis encountered an error: {str(e)}"]

    def _parse_output(self, raw_stdout: str) -> list[str]:
        diagnoses = []
        for line in raw_stdout.splitlines():
            line = line.strip()
            if "🔍" in line:
                diagnoses.append(line)
        return diagnoses


async def main():
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

    print("正在启动 Joern 容器进行异步分析...")
    results = await advisor.analyze_code(test_code)
    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
