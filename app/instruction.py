from aiogram.utils.markdown import hlink


async def text_instruction():
       androidLink = hlink('Android', 'https://play.google.com/store/apps/details?id=com.wireguard.android&hl=ru&gl=US')
       iOSLink = hlink('iPhone', 'https://apps.apple.com/us/app/wireguard/id1441195209?ls=1')
       windowsLink = hlink('Windows', 'https://download.wireguard.com/windows-client/wireguard-installer.exe')
       text = f"1. В меню 'Управление устройствами' добавьте новое устройство.\n" \
              "2. Скачайте файл настроек. Вызовите контекстное меню и нажмите 'Сохранить как' (для ПК) или 'Сохранить в загрузки' (для телефона)\n" \
              f"3. Установите приложение Wireguard для:\n{androidLink}, {iOSLink}, {windowsLink}.\n" \
              "4. Запустите программу Wireguard и нажмите ➕ внизу экрана справа\n" \
              "5. Нажмите кнопку “Импорт из файла или архива”, выберите скачанный конфиг файл из папки загрузок (для телефонов обычно Downloads/Telegram)\n" \
              "6. Включите тумблер.\n\n"\
              "Об оплате:\n"\
              "Для обеспечения безопасности финансовые операции производятся средствами Telegram и Яндекс.Кассы(ЮMoney). Данные карт не передаются третьим лицам и нашему сервису. С нашей стороны мы видим только статус оплаты.\n" \
              "При выполнении операции от вас потребуется адрес электронной почты, куда сервис ЮMoney вышлет чек об оплате.\n" \
              "Оплата производится в меню 'Управление устройствами'. Стоимость предоставления услуг составляет 120 рублей за 31 календарный день."
       return text

