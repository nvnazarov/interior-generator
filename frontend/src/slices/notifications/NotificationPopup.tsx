import moment from "moment";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import "./NotificationPopup.scss";
import { useAppSelector } from "../storeTypes";
import { selectLastNotification, type Notification } from "./slice";

export function NotificationPopup() {
  const notification = useAppSelector(selectLastNotification);
  const [notifications, setNotifications] = useState<
    (Notification & { id: string })[]
  >([]);

  useEffect(() => {
    if (notification) {
      const id = uuidv4();
      setNotifications((prev) => [...prev, { ...notification, id }]);
      setTimeout(() => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
      }, 5000);
    }
  }, [notification]);

  return (
    <div className="notification-popup__container">
      <AnimatePresence mode="popLayout">
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            className={
              notification.severity === "error"
                ? "notification-popup__item--error"
                : "notification-popup__item"
            }
            initial={{ opacity: 0, y: -50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            layout
          >
            <p>{notification.text}</p>
            <span>{moment(notification.date).fromNow()}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
