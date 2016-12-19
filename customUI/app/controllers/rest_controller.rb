class RestController < ApplicationController
  def openhab_getitems
  	require 'net/http'

	url = URI.parse('http://localhost/rest/items')
	req = Net::HTTP::Get.new(url.to_s)
	res = Net::HTTP.start(url.host, url.port) {|http|
	  http.request(req)
	}
  	itemArray = res.body.split('},{')
  	tempArray = Array.new(itemArray.length()-1)
  	finalArray = Array.new(itemArray.length()-1)
  	i = 1
  	while i < itemArray.length() do
  		tempArray[i-1] = itemArray[i].split('","')
  		item = Array.new(2) #type, name
  		j = 0
  		while j < tempArray[i-1].length() do
			temp = tempArray[i-1][j].split('":"')
			if temp[0] == "type"
				item[0] = temp[1]
			end
			if temp[0] == "name"
				item[1] = temp[1]
			end
			j += 1
  		end
  		finalArray[i-1] = item
  		i += 1
  	end
  	
  	render json: res.body
  end
  def openhab_sendcommand
  	data = "#{request.body.read}"
  	
  	dataArray = data.split(' ')
  	item = dataArray[0]
  	command = dataArray[1]
  	require 'net/http'

	url = URI.parse("http://localhost/rest/items/"+item)
	http = Net::HTTP.new(url.host, url.port)
	req = Net::HTTP::POST.new(url.path, {'Content-Type' => 'text/plain'})
	req.body = command
	res = http.request(req)
  	render text: res
  end
end
