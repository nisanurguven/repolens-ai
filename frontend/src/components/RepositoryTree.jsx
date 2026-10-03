import { useState } from "react";

function RepositoryTree({ node, level = 0 }) {
  const [isOpen, setIsOpen] = useState(level < 2);

  const isDirectory = node.type === "directory";

  function handleToggle() {
    if (isDirectory) {
      setIsOpen((currentValue) => !currentValue);
    }
  }

  return (
    <div>
      <div
        className="tree-row"
        style={{
          paddingLeft: `${level * 18}px`,
        }}
        onClick={handleToggle}
      >
        <span className="tree-icon">
          {isDirectory ? (isOpen ? "📂" : "📁") : "📄"}
        </span>

        <span className="tree-name">
          {node.name}
        </span>

        {!isDirectory && node.size !== undefined && (
          <span className="tree-size">
            {formatFileSize(node.size)}
          </span>
        )}
      </div>

      {isDirectory && isOpen && node.children && (
        <div>
          {node.children.map((child) => (
            <RepositoryTree
              key={child.path}
              node={child}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function formatFileSize(bytes) {
  if (bytes === null || bytes === undefined) {
    return "";
  }

  if (bytes < 1024) {
    return `${bytes} B`;
  }

  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default RepositoryTree;