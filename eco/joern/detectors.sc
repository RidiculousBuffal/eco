
@main def main(cpgPath: String) = {
    importCpg(cpgPath)

    println("=" * 20)
    println(s"开始分析 CPG: $cpgPath")
    println("=" * 20)

    // 运行所有检测并直接打印结果
    println("\n[1] 检测递归:")
    detectRecursion().foreach(res => println(s"  🔍 $res"))

    println("\n[2] 检测静态 Vector:")
    detectStaticVector().foreach(res => println(s"  🔍 $res"))

    println("\n[3] 检测慢速 I/O:")
    detectSlowIO().foreach(res => println(s"  🔍 $res"))

    println("\n[4] 检测循环不变量:")
    detectLoopInvariant().foreach(res => println(s"  🔍 $res"))
}

def detectRecursion(): List[String] = {
    cpg.method.filter { m =>
        m.callOut.exists(_.methodFullName == m.fullName)
    }.filterNot { m =>
        m.local.exists(l =>
            l.typeFullName.contains("array") ||
            l.typeFullName.contains("map") ||
            l.typeFullName.contains("unordered_map")
        )
    }.map { m =>
        s"Method ${m.name} at lines ${m.lineNumber.getOrElse(0)} uses pure recursion."
    }.l
}

def detectStaticVector(): List[String] = {
    cpg.local.filter(_.typeFullName.contains("vector")).filterNot { vec =>
        val calls = vec.referencingIdentifiers.inCall.name.toSet
        val dynamicOps = Set("push_back", "pop_back", "insert", "erase", "resize")
        calls.intersect(dynamicOps).nonEmpty
    }.map { vec =>
        s"Vector '${vec.name}' at line ${vec.lineNumber.getOrElse(0)} is static."
    }.l
}

def detectSlowIO(): List[String] = {
    // 1. 获取所有涉及 cin/cout 的调用
    val fromCode = cpg.call.filter(c => c.code.contains("cin") || c.code.contains("cout"))
    // 2. 获取所有流式操作符
    val fromName = cpg.call.name("operator<<", "operator>>")

    // 合并并按行号分组
    (fromCode.toSet ++ fromName.toSet)
        .groupBy(_.lineNumber.getOrElse(0)) // 按行号聚类
        .toList
        .filter(_._1 > 0) // 过滤掉无效行号
        .sortBy(_._1)     // 按行号排序
        .map { case (line, calls) =>
            // 每一行只取 code 最长的那一个节点（通常是完整的语句）
            val fullStatement = calls.maxBy(_.code.length).code
            s"Slow I/O detected at line $line: $fullStatement"
        }
}




def detectLoopInvariant(): List[String] = {
    cpg.controlStructure.filter(_.controlStructureType.matches("FOR|WHILE")).flatMap { loop =>
        val expensiveCalls = Set("sort", "find", "pow", "sqrt")
        loop.ast.isCall.filter(call => expensiveCalls.exists(call.name.contains)).map { call =>
            s"Expensive call '${call.name}' at line ${call.lineNumber.getOrElse(0)} inside loop."
        }
    }.l
}
