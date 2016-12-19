Rails.application.routes.draw do
  get 'rest/openhab_getitems'
  get 'main/application'
  root 'main#application'
  match '/rest/getitems' => 'rest#openhab_getitems', via: :get
  match '/rest/sendcommand' => 'rest#openhab_sendcommand', via: :post


  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end
