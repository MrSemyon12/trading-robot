export const parseDateTime = (datetime) => {
  const date = new Date(datetime);
  return date.toLocaleString("ru-RU");
};
