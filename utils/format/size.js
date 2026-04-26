function bytesToMB(bytes) {
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function bytesToGB(bytes) {
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

function tamanoLegible(bytes) {
  if (bytes < 1024) return bytes + ' B';
  else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  else if (bytes < 1024 * 1024 * 1024) return (bytes / (1024*1024)).toFixed(2) + ' MB';
  else return (bytes / (1024*1024*1024)).toFixed(2) + ' GB';
}

module.exports = { bytesToMB, bytesToGB, tamanoLegible };
